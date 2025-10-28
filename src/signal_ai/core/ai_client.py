import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.generative_models import ChatSession
from tenacity import retry, stop_after_attempt, wait_exponential


class AIClient:
    """Handles all interactions with the AI model."""

    def __init__(self, api_key: str):
        """
        Initializes the AIClient.

        Args:
            api_key: The API key for the AI service.
        """
        self._api_key = api_key
        genai.configure(api_key=self._api_key)
        system_instruction = (
            "You are an AI assistant. Your primary goal is to provide clear, concise, and helpful answers.\n\n"
            "**Core Rules:**\n"
            "1. **Use Simple Language:** Your top priority is to be understood. Avoid all jargon, academic language, and overly complex phrasing. Explain things in the simplest possible terms.\n"
            "2. **Be Concise:** Your response must be a single paragraph. Do not use lists, titles, or multiple paragraphs.\n"
            "3. **Answer the Question Directly:** Get straight to the point. Do not ramble or provide unnecessary background information.\n"
            "4. **Handle Greetings Simply:** If the user says hello or asks how you are, respond with a simple, direct, and friendly greeting. Do not analyze the question."
        )
        self.model = self._get_generative_model("gemini-flash-latest", system_instruction=system_instruction)
        self._chat_sessions: Dict[str, ChatSession] = {}
        logging.info("AIClient initialized.")

    def _get_generative_model(self, model_name: str, system_instruction: Optional[str] = None) -> genai.GenerativeModel:
        """Retrieves a generative model."""
        logging.info(f"Initializing model: {model_name}")
        return genai.GenerativeModel(model_name, system_instruction=system_instruction)

    def _get_chat_session(self, chat_id: str, history: List[Dict[str, Any]]) -> ChatSession:
        """
        Retrieves or creates a chat session for a given chat ID.

        Args:
            chat_id: The unique identifier for the chat.
            history: The chat history to initialize the session with.

        Returns:
            The ChatSession object.
        """
        # Always create a new chat session for each request to ensure isolation
        logging.info(f"Creating new chat session for chat_id: {chat_id}")
        return self.model.start_chat(history=history)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(
        self, chat_id: str, prompt: str, history: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a response from the AI model.

        Args:
            chat_id: The unique identifier for the chat.
            prompt: The input prompt for the AI.
            history: The chat history.

        Returns:
            The AI-generated response.
        """
        logging.info(f"Generating AI response for chat_id: {chat_id}, prompt: '{prompt}'")
        try:
            chat_session = self._get_chat_session(chat_id, history)
            response = await chat_session.send_message_async(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error generating AI response: {e}", exc_info=True)
            if chat_id in self._chat_sessions:
                del self._chat_sessions[chat_id]
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response_stream(
        self, chat_id: str, prompt: str, history: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from the AI model.

        Args:
            chat_id: The unique identifier for the chat.
            prompt: The input prompt for the AI.
            history: The chat history.

        Yields:
            Chunks of the AI-generated response as they become available.
        """
        logging.info(f"Generating AI stream for chat_id: {chat_id}, prompt: '{prompt}'")
        try:
            chat_session = self._get_chat_session(chat_id, history)
            stream = await chat_session.send_message_async(prompt, stream=True)
            async for chunk in stream:
                yield chunk.text
        except Exception as e:
            logging.error(f"Error generating AI stream: {e}", exc_info=True)
            if chat_id in self._chat_sessions:
                del self._chat_sessions[chat_id]
            raise
