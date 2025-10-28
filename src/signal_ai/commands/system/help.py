from typing import Optional
from signalbot import Command, Context, regex_triggered


class HelpCommand(Command):
    def describe(self) -> str:
        return "Shows the available command namespaces."

    @regex_triggered(r"^!help(?: (\w+))?$")
    async def handle(self, c: Context, namespace: Optional[str] = None) -> None:
        # This will be updated to dynamically list namespaces
        help_text = """
*Available Command Namespaces*
- `!system`: Core bot operations.
- `!config`: Bot settings management.
- `!context`: Conversation context management.
- `!memory`: Long-term memory management.
- `!task`: Task and reminder management.
- `!ai`: Direct AI model interactions.
- `!utility`: Miscellaneous tools.

Run `!system help [namespace]` for more information on a specific command.
"""
        await c.reply(help_text, text_mode="styled")
