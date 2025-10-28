from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.persistence import PersistenceManager


class MemoryCommand(Command):
    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager

    def describe(self) -> str:
        return "Manages the bot's long-term memory for this chat."

    @regex_triggered(r"^!memory(?: (set|clear)(?: (.+))?)?$")
    async def handle(
        self, c: Context, sub_command: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        if not sub_command:
            chat_context = self._persistence_manager.load_context(c.message.source)
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

        chat_context = self._persistence_manager.load_context(c.message.source)

        if sub_command == "set":
            if not value:
                await c.reply("Usage: `!memory set [text]`", text_mode="styled")
                return

            chat_context.pinned_message = value
            self._persistence_manager.save_context(c.message.source)
            await c.reply(
                f"**Pinned message updated:**\n{value}", text_mode="styled"
            )

        elif sub_command == "clear":
            chat_context.pinned_message = ""
            self._persistence_manager.save_context(c.message.source)
            await c.reply("Pinned message cleared.", text_mode="styled")
