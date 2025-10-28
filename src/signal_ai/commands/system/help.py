from typing import cast, Dict, Any
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class HelpCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Shows available commands."

    async def handle(self, c: Context, args: Dict[str, Any]) -> None:
        bot = cast("SignalAIBot", c.bot)
        tool_manager = bot.tool_manager
        if not tool_manager:
            await c.reply("Tool manager not available.")
            return

        command_name = args.get("command_name")
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

        await c.reply(help_text, text_mode="styled")
