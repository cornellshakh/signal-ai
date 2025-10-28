from typing import List, cast
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


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

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        persistence_manager = bot.persistence_manager
        if not persistence_manager:
            await c.reply("Persistence manager not available.")
            return

        if not args:
            await c.reply("Usage: `!config [view|set] [key] [value]`", text_mode="styled")
            return

        sub_command = args[0]
        chat_context = persistence_manager.load_context(c.message.source)

        if sub_command == "view":
            mode = chat_context.config.mode
            await c.reply(f"Current mode: `{mode}`", text_mode="styled")

        elif sub_command == "set":
            if len(args) < 3:
                await c.reply(
                    "Usage: `!config set mode [ai|mention|quiet]`", text_mode="styled"
                )
                return

            key = args[1]
            value = args[2]

            if key.lower() == "mode":
                new_mode = value.lower()
                if new_mode in ["ai", "mention", "quiet"]:
                    chat_context.config.mode = new_mode
                    persistence_manager.save_context(c.message.source)
                    await c.reply(f"Mode set to `{new_mode}`.", text_mode="styled")
                else:
                    await c.reply(
                        f"Invalid mode: `{new_mode}`. Must be one of `ai`, `mention`, or `quiet`.",
                        text_mode="styled",
                    )
            else:
                await c.reply(f"Unknown config key: `{key}`.", text_mode="styled")
        else:
            await c.reply(f"Unknown subcommand: `{sub_command}`.", text_mode="styled")
