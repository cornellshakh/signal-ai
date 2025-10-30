from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict, List, Any, Optional, AsyncGenerator

import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel, ChatSession
from google.generativeai.types import (
    ContentDict,
    AsyncGenerateContentResponse,
    FunctionDeclaration,
)
from google.ai.generativelanguage_v1beta.types.generative_service import (
    GenerateContentResponse,
)
from google.api_core import exceptions as api_core_exceptions
import structlog
import redis
from redis.exceptions import RedisError
from cachetools import LRUCache
from tenacity import retry, stop_after_attempt, wait_exponential

from .prompt_manager import PromptManager
from .memory_manager import MemoryManager


log = structlog.get_logger()


class AIClient:
    """Handles all interactions with the AI model."""

    def __init__(
        self,
        api_key: str,
        prompt_manager: PromptManager,
        memory_manager: MemoryManager,
        redis_host: str = "redis",
        redis_port: int = 6379,
    ):
        """
        Initializes the AIClient.

        Args:
            api_key: The API key for the AI service.
            prompt_manager: The prompt manager instance.
            memory_manager: The memory manager instance.
        """
        self._api_key = api_key
        self.prompt_manager = prompt_manager
        self.memory_manager = memory_manager
        genai.configure(api_key=self._api_key)
        self.model = self._get_generative_model("gemini-flash-latest")
        self._chat_sessions: LRUCache[str, ChatSession] = LRUCache(maxsize=100)
        self._redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        log.info("AIClient initialized.")

    def _get_generative_model(
        self,
        model_name: str,
        tools: Optional[List[Any]] = None,
    ) -> "GenerativeModel":
        """Retrieves a generative model."""
        log.info("model.init", model_name=model_name)
        return GenerativeModel(
            model_name,
            tools=tools,
        )

    async def _get_chat_session(
        self, chat_id: str, initial_history: List[ContentDict]
    ) -> ChatSession:
        """
        Retrieves or creates a chat session for a given chat ID using a multi-level cache.
        """
        # Level 1: In-memory LRU cache (hot)
        if chat_id in self._chat_sessions:
            log.info("cache.hot.hit", chat_id=chat_id)
            return self._chat_sessions[chat_id]

        # Level 2: Redis cache (warm)
        try:
            cached_history_json = await self._redis.get(chat_id)
            if cached_history_json:
                log.info("cache.warm.hit", chat_id=chat_id)
                cached_history = json.loads(cached_history_json.decode("utf-8"))
                chat_session = self.model.start_chat(history=cached_history)
                self._chat_sessions[chat_id] = chat_session
                return chat_session
        except RedisError as e:
            log.error("redis.error", error=e, exc_info=True)

        # Level 3: Initial history from TinyDB (cold)
        log.info("cache.miss", chat_id=chat_id)
        chat_session = self.model.start_chat(history=initial_history)
        self._chat_sessions[chat_id] = chat_session
        return chat_session

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self, chat_id: str, prompt: str, history: List[ContentDict]
    ) -> str:
        """
        Generates a response from the AI model.
        """
        log.info("ai.response.start", chat_id=chat_id, prompt=prompt)
        try:
            chat_session = await self._get_chat_session(chat_id, history)
            response = await chat_session.send_message_async(prompt)
            self._update_caches(chat_id, chat_session.history)
            if response.candidates:
                return response.candidates[0].content.parts[0].text
            log.warning("ai.response.no_candidates")
            return ""
        except (
            api_core_exceptions.GoogleAPICallError,
            api_core_exceptions.InvalidArgument,
        ) as e:
            log.error("ai.response.api.error", error=e, exc_info=True)
            raise
        except Exception as e:
            log.error("ai.response.unexpected.error", error=e, exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response_stream(
        self, chat_id: str, prompt: str, history: List[ContentDict]
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from the AI model.
        """
        log.info("ai.stream.start", chat_id=chat_id, prompt=prompt)
        try:
            chat_session = await self._get_chat_session(chat_id, history)
            stream = await chat_session.send_message_async(prompt, stream=True)
            async for chunk in stream:
                yield chunk.text
            self._update_caches(chat_id, chat_session.history)
        except (
            api_core_exceptions.GoogleAPICallError,
            api_core_exceptions.InvalidArgument,
        ) as e:
            log.error("ai.stream.api.error", error=e, exc_info=True)
            raise
        except Exception as e:
            log.error("ai.stream.unexpected.error", error=e, exc_info=True)
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
            log.info("cache.update", chat_id=chat_id)
        except RedisError as e:
            log.error("redis.error", error=e, exc_info=True)
        except Exception as e:
            log.error("cache.serialization.error", chat_id=chat_id, error=e, exc_info=True)

    def clear_chat_session(self, chat_id: str):
        """
        Clears a specific chat session from all caches (in-memory and Redis).
        """
        # Clear from in-memory LRU cache
        if chat_id in self._chat_sessions:
            del self._chat_sessions[chat_id]
            log.info("cache.clear.in_memory", chat_id=chat_id)

        # Clear from Redis cache
        try:
            self._redis.delete(chat_id)
            log.info("cache.clear.redis", chat_id=chat_id)
        except RedisError as e:
            log.error("redis.error", error=e, exc_info=True)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response_with_tools(
        self,
        chat_id: str,
        prompt: str,
        history: List[ContentDict],
        tool_schemas: List[FunctionDeclaration],
    ) -> AsyncGenerateContentResponse:
        """
        Generates a response from the AI model, making it aware of available tools.
        """
        log.info("ai.response.tool.start", chat_id=chat_id, prompt=prompt)
        if not prompt:
            # Return an empty response if the prompt is empty, as the SDK will raise an error.
            # The reasoning engine will interpret this as the end of the conversation.
            return AsyncGenerateContentResponse(
                done=True,
                iterator=None,
                result=GenerateContentResponse(),
            )

        try:
            # Re-initialize the model with the provided tool schemas for this specific call
            model_with_tools = self._get_generative_model(
                "gemini-flash-latest",
                tools=tool_schemas,
            )
            system_instruction = self.prompt_manager.get("system_instruction")
            full_history: List[ContentDict] = [
                ContentDict(role="user", parts=[{"text": system_instruction}]),
                ContentDict(role="model", parts=[{"text": "OK"}]),
            ] + history
            chat_session = model_with_tools.start_chat(history=full_history)
            response = await chat_session.send_message_async(prompt)

            # We are not updating the main history cache here yet, as the reasoning loop will handle that.
            return response
        except (
            api_core_exceptions.GoogleAPICallError,
            api_core_exceptions.InvalidArgument,
        ) as e:
            log.error("ai.response.tool.api.error", error=e, exc_info=True)
            raise
        except Exception as e:
            log.error("ai.response.tool.unexpected.error", error=e, exc_info=True)
            raise
