import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator

import google.generativeai as genai
import redis
from cachetools import LRUCache
from google.generativeai.generative_models import ChatSession
from tenacity import retry, stop_after_attempt, wait_exponential

from .prompt_manager import PromptManager


class AIClient:
    """Handles all interactions with the AI model."""

    def __init__(self, api_key: str, prompt_manager: PromptManager, redis_host: str = "redis", redis_port: int = 6379):
        """
        Initializes the AIClient.

        Args:
            api_key: The API key for the AI service.
            prompt_manager: The prompt manager instance.
        """
        self._api_key = api_key
        genai.configure(api_key=self._api_key)
        system_instruction = prompt_manager.get("system_instruction")
        self.model = self._get_generative_model("gemini-flash-latest", system_instruction=system_instruction)
        self._chat_sessions: LRUCache[str, ChatSession] = LRUCache(maxsize=100)
        self._redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        logging.info("AIClient initialized.")

    def _get_generative_model(self, model_name: str, system_instruction: Optional[str] = None) -> genai.GenerativeModel:
        """Retrieves a generative model."""
        logging.info(f"Initializing model: {model_name}")
        return genai.GenerativeModel(model_name, system_instruction=system_instruction)

    def _get_chat_session(self, chat_id: str, initial_history: List[Dict[str, Any]]) -> ChatSession:
        """
        Retrieves or creates a chat session for a given chat ID using a multi-level cache.
        """
        # Level 1: In-memory LRU cache (hot)
        if chat_id in self._chat_sessions:
            logging.info(f"Hot cache hit for chat_id: {chat_id}")
            return self._chat_sessions[chat_id]

        # Level 2: Redis cache (warm)
        try:
            cached_history_json = self._redis.get(chat_id)
            if cached_history_json:
                logging.info(f"Warm cache hit for chat_id: {chat_id}")
                cached_history = json.loads(cached_history_json)
                chat_session = self.model.start_chat(history=cached_history)
                self._chat_sessions[chat_id] = chat_session
                return chat_session
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error on get: {e}", exc_info=True)

        # Level 3: Initial history from TinyDB (cold)
        logging.info(f"Cold cache miss for chat_id: {chat_id}")
        chat_session = self.model.start_chat(history=initial_history)
        self._chat_sessions[chat_id] = chat_session
        return chat_session

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(
        self, chat_id: str, prompt: str, history: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a response from the AI model.
        """
        logging.info(f"Generating AI response for chat_id: {chat_id}, prompt: '{prompt}'")
        try:
            chat_session = self._get_chat_session(chat_id, history)
            response = await chat_session.send_message_async(prompt)
            self._update_caches(chat_id, chat_session.history)
            return response.text
        except Exception as e:
            logging.error(f"Error generating AI response: {e}", exc_info=True)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response_stream(
        self, chat_id: str, prompt: str, history: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from the AI model.
        """
        logging.info(f"Generating AI stream for chat_id: {chat_id}, prompt: '{prompt}'")
        try:
            chat_session = self._get_chat_session(chat_id, history)
            stream = await chat_session.send_message_async(prompt, stream=True)
            async for chunk in stream:
                yield chunk.text
            self._update_caches(chat_id, chat_session.history)
        except Exception as e:
            logging.error(f"Error generating AI stream: {e}", exc_info=True)
            raise

    def _update_caches(self, chat_id: str, history: List[Any]):
        """
        Updates the Redis cache with the latest history.
        """
        try:
            # Convert the history of Content objects to a JSON-serializable list of dicts
            serializable_history = [
                {"role": msg.role, "parts": [part.text for part in msg.parts]}
                for msg in history
            ]
            history_json = json.dumps(serializable_history)
            self._redis.set(chat_id, history_json)
            logging.info(f"Updated Redis cache for chat_id: {chat_id}")
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error on set: {e}", exc_info=True)
        except Exception as e:
            logging.error(
                f"Failed to serialize and cache history for chat_id {chat_id}: {e}",
                exc_info=True,
            )

    def clear_chat_session(self, chat_id: str):
        """
        Clears a specific chat session from all caches (in-memory and Redis).
        """
        # Clear from in-memory LRU cache
        if chat_id in self._chat_sessions:
            del self._chat_sessions[chat_id]
            logging.info(f"Cleared in-memory cache for chat_id: {chat_id}")

        # Clear from Redis cache
        try:
            self._redis.delete(chat_id)
            logging.info(f"Cleared Redis cache for chat_id: {chat_id}")
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error on delete: {e}", exc_info=True)
