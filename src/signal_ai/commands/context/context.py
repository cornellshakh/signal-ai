import asyncio
import re
from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class ContextCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "context"

    @property
    def description(self) -> str:
        return "Manages the chat context."

    def help(self) -> str:
        return (
            "Usage: `!context <view|clear|new>`\n\n"
            "Manages the bot's short-term memory for the current conversation.\n\n"
            "**Subcommands:**\n"
            "- `view`: Show the current chat history.\n"
            "- `clear`: Clear the current chat history.\n"
            "- `new <prompt>`: Create a new conversation group with a prompt."
        )

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.persistence_manager or not bot.ai_client or not bot.prompt_manager:
            return ErrorResult("Persistence, AI, or prompt manager not available.")

        if not args:
            sub_command = "view"
            text = None
        else:
            sub_command = args[0]
            text = " ".join(args[1:]) if len(args) > 1 else None

        chat_context = await bot.persistence_manager.load_context(c.chat_id)

        if sub_command == "view":
            history = chat_context.history
            if not history:
                return TextResult("Chat history is empty.")

            num_messages = 10
            if text:
                try:
                    num_messages = int(text)
                except ValueError:
                    pass

            start_index = max(0, len(history) - num_messages)
            formatted_history = []
            for i, item in enumerate(history[start_index:], start=start_index + 1):
                role = item.get("role", "unknown").capitalize()
                parts = item.get("parts", [])
                content = parts[0] if parts else ""
                formatted_history.append(f"_{i}_. *{role}*:\n{content}")

            full_history = "\n\n".join(formatted_history)
            max_len = 4000
            chunks = [
                full_history[i : i + max_len]
                for i in range(0, len(full_history), max_len)
            ]

            for chunk in chunks:
                await c.raw_context.reply(chunk, text_mode="styled")
                await asyncio.sleep(1)
            return None

        elif sub_command == "clear":
            chat_context.history = []
            await bot.persistence_manager.save_context(c.chat_id)
            bot.ai_client.clear_chat_session(c.chat_id)
            return TextResult("Chat history and AI session cache have been cleared.")

        elif sub_command == "new":
            if not text:
                return ErrorResult("Usage: `!context new <prompt>`")

            try:
                group_name_prompt = bot.prompt_manager.get(
                    "generate_group_name", prompt=text
                )
                group_name = await bot.ai_client.generate_response(
                    chat_id=c.chat_id, prompt=group_name_prompt, history=[]
                )
                group_name = re.sub(r"[*_~`[\]()]", "", group_name.strip().strip('"'))

                user_uuid = c.raw_context.message.source_uuid
                if not user_uuid:
                    return ErrorResult("Could not identify your user UUID.")

                if not bot.group_manager:
                    return ErrorResult("Group manager is not configured.")

                group_info = await bot.group_manager.create(group_name, [user_uuid])
                group_id = group_info.get("id")
                if not group_id:
                    return ErrorResult("Could not retrieve the group ID.")

                await bot._detect_groups()

                group_context = await bot.persistence_manager.load_context(group_id)
                group_context.config.mode = "ai"
                await bot.persistence_manager.save_context(group_id)

                ai_response = await bot.ai_client.generate_response(
                    chat_id=group_id, prompt=text, history=[]
                )
                await bot.send(group_id, ai_response, text_mode="styled")

                return TextResult(
                    f"I've created the group '**{group_name}**' and added you to it."
                )

            except Exception as e:
                return ErrorResult(f"An error occurred: {e}")

        else:
            return ErrorResult(f"Unknown subcommand: `{sub_command}`.")