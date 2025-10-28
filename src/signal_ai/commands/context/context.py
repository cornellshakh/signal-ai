from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.persistence import PersistenceManager


class ContextCommand(Command):
    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager

    def describe(self) -> str:
        return "Manages the chat context."

    @regex_triggered(r"^!context(?: (view|clear))?$")
    async def handle(self, c: Context, sub_command: Optional[str] = None) -> None:
        if not sub_command:
            await c.reply(
                "Usage: `!context <view|clear>`\n\n"
                "**Sub-commands:**\n"
                "- `view`: Show the current chat history.\n"
                "- `clear`: Clear the current chat history.",
                text_mode="styled",
            )
            return

        chat_context = self._persistence_manager.load_context(c.message.source)

        if sub_command == "view":
            history = chat_context.history
            if not history:
                await c.reply("Chat history is empty.", text_mode="styled")
                return

            formatted_history = []
            for item in history:
                role = item.get("role", "unknown").capitalize()
                parts = item.get("parts", [])
                content = parts[0] if parts else ""
                formatted_history.append(f"**{role}:** {content}")

            await c.reply("\n\n".join(formatted_history), text_mode="styled")

        elif sub_command == "clear":
            chat_context.history = []
            self._persistence_manager.save_context(c.message.source)
            await c.reply("Chat history has been cleared.", text_mode="styled")
