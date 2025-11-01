from typing import Any, Optional

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager
from signal_ai.services.tooling import ToolingService


class HelpSchema(BaseModel):
    command_name: Optional[str] = Field(
        None, description="The name of the command to get help for."
    )


class HelpTool(BaseTool):
    """
    A tool to get help for other tools.
    """

    name = "help"
    description = "Shows available commands."
    schema = HelpSchema

    def __init__(self, tooling_service: ToolingService):
        self._tooling_service = tooling_service

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        command_name: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if command_name:
            if command_name in self._tooling_service.tools:
                tool = self._tooling_service.tools[command_name]
                help_text = f"*Help for `{tool.name}`:*\n{tool.description}"
            else:
                help_text = f"Unknown command: `{command_name}`"
        else:
            help_text = "*Available Commands:*\n"
            for name, tool in sorted(self._tooling_service.tools.items()):
                help_text += f"- `{name}`: {tool.description}\n"
            help_text += "\nRun `!help [command]` for more details."

        return help_text