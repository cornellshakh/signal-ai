from typing import cast, Dict, Any, Union, Optional

from ...bot import SignalAIBot
from ...core.command import BaseCommand, ErrorResult, TextResult
from ...core.context import AppContext


class HelpCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Shows available commands."

    @property
    def ArgsSchema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command_name": {
                    "type": "string",
                    "description": "The name of the command to get help for.",
                },
            },
        }

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        tool_manager = bot.tool_manager
        if not tool_manager:
            return ErrorResult("Tool manager not available.")

        command_name = args[0] if args else None
        if command_name:
            if command_name in tool_manager.tools:
                command = tool_manager.tools[command_name]
                help_text = command.help()
            else:
                help_text = f"Unknown command: `{command_name}`"
        else:
            help_text = "*Available Commands:*\n"
            for name, command in sorted(tool_manager.tools.items()):
                help_text += f"- `{name}`: {command.description}\n"
            help_text += "\nRun `!help [command]` for more details."

        return TextResult(help_text)