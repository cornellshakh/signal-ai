from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class ConfigCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "config"

    @property
    def description(self) -> str:
        return "Manages the bot's configuration for this chat."

    def help(self) -> str:
        return (
            "Usage: `!config [view|set] [key] [value]`\n\n"
            "Manages the bot's configuration for this chat.\n\n"
            "**Subcommands:**\n"
            "- `view`: Show the current configuration.\n"
            "- `set`: Set a configuration key.\n\n"
            "**Available keys for `set`:**\n"
            "- `mode`: Set the chat mode.\n"
            "  - `ai`: The bot will respond to all messages using the AI model.\n"
            "  - `mention`: The bot will only respond to messages where it is mentioned.\n"
            "  - `quiet`: The bot will not respond to messages unless explicitly commanded."
        )

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.persistence_manager:
            return ErrorResult("Persistence manager not available.")

        if not args:
            return ErrorResult("Usage: `!config [view|set] [key] [value]`")

        sub_command = args[0]
        chat_context = await bot.persistence_manager.load_context(c.chat_id)

        if sub_command == "view":
            mode = chat_context.config.mode
            return TextResult(f"Current mode: `{mode}`")

        elif sub_command == "set":
            if len(args) < 3:
                return ErrorResult("Usage: `!config set mode [ai|mention|quiet]`")

            key = args[1]
            value = args[2]

            if key.lower() == "mode":
                new_mode = value.lower()
                if new_mode in ["ai", "mention", "quiet"]:
                    chat_context.config.mode = new_mode
                    await bot.persistence_manager.save_context(c.chat_id)
                    return TextResult(f"Mode set to `{new_mode}`.")
                else:
                    return ErrorResult(
                        f"Invalid mode: `{new_mode}`. Must be one of `ai`, `mention`, or `quiet`."
                    )
            else:
                return ErrorResult(f"Unknown config key: `{key}`.")
        else:
            return ErrorResult(f"Unknown subcommand: `{sub_command}`.")