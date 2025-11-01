from typing import Any

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class ImageSchema(BaseModel):
    prompt: str = Field(..., description="The prompt to generate an image from.")


class ImageTool(BaseTool):
    """
    Generates an image based on a prompt.
    """

    name = "image"
    description = "Generates an image based on a prompt."
    schema = ImageSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        return await ai_client.generate_response(
            chat_id=context.chat_id,
            prompt=f"Create an image based on the prompt: {prompt}",
            history=[],
        )