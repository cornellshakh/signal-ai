from typing import Any, Optional

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class ConfigSchema(BaseModel):
    sub_command: str = Field(
        "view", description="The subcommand to run (set, view)."
    )
    key: Optional[str] = Field(None, description="The config key to set.")
    value: Optional[str] = Field(None, description="The value to set.")


class ConfigTool(BaseTool):
    """
    Manages the bot's configuration for this chat.
    """

    name = "config"
    description = "Manages the bot's configuration for this chat."
    schema = ConfigSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        sub_command: str = "view",
        key: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if sub_command == "view":
            mode = context.config.mode
            return f"Current mode: `{mode}`"

        elif sub_command == "set":
            if not key or not value:
                return "Usage: `!config set mode [ai|mention|quiet]`"

            if key.lower() == "mode":
                new_mode = value.lower()
                if new_mode in ["ai", "mention", "quiet"]:
                    context.config.mode = new_mode
                    await state_manager.save_context(context)
                    return f"Mode set to `{new_mode}`."
                else:
                    return f"Invalid mode: `{new_mode}`. Must be one of `ai`, `mention`, or `quiet`."
            else:
                return f"Unknown config key: `{key}`."
        else:
            return f"Unknown subcommand: `{sub_command}`."