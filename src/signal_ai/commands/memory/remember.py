from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class RememberCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "remember"

    @property
    def description(self) -> str:
        return "Manages the bot's long-term memory for this chat."

    def help(self) -> str:
        return (
            "Usage: `!remember [set|clear] [text]`\n\n"
            "Manages the bot's long-term memory for this chat.\n"
            "This is a 'pinned message' that will be included in all future AI interactions.\n\n"
            "**Subcommands:**\n"
            "- `set [text]`: Set the pinned message.\n"
            "- `clear`: Clear the pinned message."
        )

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.persistence_manager:
            return ErrorResult("Persistence manager not available.")

        if not args:
            sub_command = "view"
            text = None
        else:
            sub_command = args[0]
            text = " ".join(args[1:]) if len(args) > 1 else None

        chat_context = await bot.persistence_manager.load_context(c.chat_id)

        if sub_command == "view":
            if chat_context.pinned_message:
                return TextResult(
                    f"**Current Pinned Message:**\n{chat_context.pinned_message}"
                )
            else:
                return TextResult(
                    "There is no pinned message. Use `!remember set [text]` to set one."
                )

        elif sub_command == "set":
            if not text:
                return ErrorResult("Usage: `!remember set [text]`")

            chat_context.pinned_message = text
            await bot.persistence_manager.save_context(c.chat_id)
            return TextResult(f"**Pinned message updated:**\n{text}")

        elif sub_command == "clear":
            chat_context.pinned_message = ""
            await bot.persistence_manager.save_context(c.chat_id)
            return TextResult("Pinned message cleared.")
        else:
            return ErrorResult(f"Unknown subcommand: `{sub_command}`.")