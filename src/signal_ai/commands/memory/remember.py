from typing import cast, Optional, Dict, Any
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class MemoryCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "memory"

    @property
    def description(self) -> str:
        return "Manages the bot's long-term memory for this chat."

    @property
    def ArgsSchema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "sub_command": {
                    "type": "string",
                    "description": "The subcommand to execute (set or clear).",
                },
                "text": {"type": "string", "description": "The text to remember."},
            },
        }

    def help(self) -> str:
        return (
            "Usage: `!memory [set|clear] [text]`\n\n"
            "Manages the bot's long-term memory for this chat.\n"
            "This is a 'pinned message' that will be included in all future AI interactions.\n\n"
            "**Subcommands:**\n"
            "- `set [text]`: Set the pinned message.\n"
            "- `clear`: Clear the pinned message."
        )

    async def handle(self, c: Context, args: Dict[str, Any]) -> None:
        bot = cast("SignalAIBot", c.bot)
        persistence_manager = bot.persistence_manager
        if not persistence_manager:
            await c.reply("Persistence manager not available.")
            return

        sub_command = args.get("sub_command")
        text = args.get("text")

        if not sub_command:
            chat_context = persistence_manager.load_context(c.message.source)
            if chat_context.pinned_message:
                await c.reply(
                    f"**Current Pinned Message:**\n{chat_context.pinned_message}",
                    text_mode="styled",
                )
            else:
                await c.reply(
                    "There is no pinned message. Use `!memory set [text]` to set one.",
                    text_mode="styled",
                )
            return

        chat_context = persistence_manager.load_context(c.message.source)

        if sub_command == "set":
            if not text:
                await c.reply("Usage: `!memory set [text]`", text_mode="styled")
                return

            chat_context.pinned_message = text
            persistence_manager.save_context(c.message.source)
            await c.reply(f"**Pinned message updated:**\n{text}", text_mode="styled")

        elif sub_command == "clear":
            chat_context.pinned_message = ""
            persistence_manager.save_context(c.message.source)
            await c.reply("Pinned message cleared.", text_mode="styled")
        else:
            await c.reply(f"Unknown subcommand: `{sub_command}`.", text_mode="styled")
