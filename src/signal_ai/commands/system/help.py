from typing import List, cast
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

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        dispatcher = bot.dispatcher
        if not dispatcher:
            await c.reply("Command dispatcher not available.")
            return

        if args:
            command_name = args[0]
            if command_name in dispatcher.commands:
                command = dispatcher.commands[command_name]
                help_text = command.help()
            else:
                help_text = f"Unknown command: `{command_name}`"
        else:
            help_text = "*Available Commands:*\n"
            for name, command in sorted(dispatcher.commands.items()):
                help_text += f"- `{name}`: {command.description}\n"
            help_text += "\nRun `!help [command]` for more details."

        await c.reply(help_text, text_mode="styled")
