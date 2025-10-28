import logging
import google.generativeai as genai


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
        self.model = self._get_generative_model()
        logging.info("AIClient initialized.")

    def _get_generative_model(self):
        """Retrieves the first available generative model."""
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                logging.info(f"Using model: {m.name}")
                return genai.GenerativeModel(m.name)
        raise ValueError("No suitable generative model found.")

    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the AI model.

        Args:
            prompt: The input prompt for the AI.

        Returns:
            The AI-generated response.
        """
        logging.info(f"Generating AI response for prompt: '{prompt}'")
        response = await self.model.generate_content_async(prompt)
        return response.text
