from typing import List, cast
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class ContextCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "context"

    @property
    def description(self) -> str:
        return "Manages the chat context."

    def help(self) -> str:
        return (
            "Usage: `!context <view|clear>`\n\n"
            "Manages the bot's short-term memory for the current conversation.\n\n"
            "**Subcommands:**\n"
            "- `view`: Show the current chat history.\n"
            "- `clear`: Clear the current chat history."
        )

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        persistence_manager = bot.persistence_manager
        ai_client = bot.ai_client

        if not persistence_manager:
            await c.reply("Persistence manager not available.")
            return

        if not args:
            await c.reply(
                "Usage: `!context <view|clear>`\n\n"
                "**Sub-commands:**\n"
                "- `view`: Show the current chat history.\n"
                "- `clear`: Clear the current chat history.",
                text_mode="styled",
            )
            return

        sub_command = args[0]
        chat_context = persistence_manager.load_context(c.message.source)

        if sub_command == "view":
            history = chat_context.history
            if not history:
                await c.reply("Chat history is empty.", text_mode="styled")
                return

            # Default to the last 10 messages
            try:
                num_messages = int(args[1]) if len(args) > 1 else 10
            except ValueError:
                num_messages = 10

            # Get the requested number of messages, or all if there are fewer
            start_index = max(0, len(history) - num_messages)

            formatted_history = []
            for i, item in enumerate(history[start_index:], start=start_index + 1):
                role = item.get("role", "unknown").capitalize()
                parts = item.get("parts", [])
                content = parts[0] if parts else ""
                formatted_history.append(f"_{i}_. *{role}*:\n{content}")

            full_history = "\n\n".join(formatted_history)

            # Split the message into chunks of 4000 characters
            max_len = 4000
            chunks = [
                full_history[i : i + max_len]
                for i in range(0, len(full_history), max_len)
            ]

            import asyncio

            for chunk in chunks:
                await c.reply(chunk, text_mode="styled")
                await asyncio.sleep(1)

        elif sub_command == "clear":
            # Clear the history in the database
            chat_context.history = []
            persistence_manager.save_context(c.message.source)

            # Clear the chat session from the AI client's cache
            if ai_client:
                ai_client.clear_chat_session(c.message.source)

            await c.reply(
                "Chat history and AI session cache have been cleared.",
                text_mode="styled",
            )
        else:
            await c.reply(f"Unknown subcommand: `{sub_command}`.", text_mode="styled")
