from typing import Any, Optional

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class RememberSchema(BaseModel):
    sub_command: str = Field(
        "view", description="The subcommand to run (set, clear, view)."
    )
    text: Optional[str] = Field(None, description="The text to remember.")


class RememberTool(BaseTool):
    """
    Manages the bot's long-term memory for this chat.
    """

    name = "remember"
    description = "Manages the bot's long-term memory for this chat."
    schema = RememberSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        sub_command: str = "view",
        text: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if sub_command == "view":
            if context.pinned_message:
                return f"**Current Pinned Message:**\n{context.pinned_message}"
            else:
                return "There is no pinned message. Use `!remember set [text]` to set one."

        elif sub_command == "set":
            if not text:
                return "Usage: `!remember set [text]`"

            context.pinned_message = text
            await state_manager.save_context(context)
            return f"**Pinned message updated:**\n{text}"

        elif sub_command == "clear":
            context.pinned_message = ""
            await state_manager.save_context(context)
            return "Pinned message cleared."
        else:
            return f"Unknown subcommand: `{sub_command}`."