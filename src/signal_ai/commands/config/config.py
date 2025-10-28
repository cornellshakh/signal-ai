from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.persistence import PersistenceManager


class ConfigCommand(Command):
    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager

    def describe(self) -> str:
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
            "  - `ai`: The bot will respond to messages using the AI model.\n"
            "  - `quiet`: The bot will not respond to messages unless explicitly commanded.\n"
            "  - `parrot`: The bot will repeat any message it receives."
        )

    @regex_triggered(r"^!config(?: (view|set)(?: (\w+)(?: (.+))?)?)?$")
    async def handle(
        self,
        c: Context,
        sub_command: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        if not sub_command:
            await c.reply("Usage: `!config [view|set] [key] [value]`", text_mode="styled")
            return

        chat_context = self._persistence_manager.load_context(c.message.source)

        if sub_command == "view":
            mode = chat_context.config.mode
            await c.reply(f"Current mode: `{mode}`", text_mode="styled")

        elif sub_command == "set":
            if not key or not value:
                await c.reply(
                    "Usage: `!config set mode [ai|quiet|parrot]`", text_mode="styled"
                )
                return

            if key.lower() == "mode":
                new_mode = value.lower()
                if new_mode in ["ai", "quiet", "parrot"]:
                    chat_context.config.mode = new_mode
                    self._persistence_manager.save_context(c.message.source)
                    await c.reply(f"Mode set to `{new_mode}`.", text_mode="styled")
                else:
                    await c.reply(
                        f"Invalid mode: `{new_mode}`. Must be one of `ai`, `quiet`, or `parrot`.",
                        text_mode="styled",
                    )
            else:
                await c.reply(f"Unknown config key: `{key}`.", text_mode="styled")
