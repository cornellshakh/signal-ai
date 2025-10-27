from typing import TYPE_CHECKING
from signalbot import Context

if TYPE_CHECKING:
    from ..bot import SignalAIBot


async def config_command_handler(context: Context, args: list[str]):
    """
    Handles the 'config' command and its sub-commands.
    """
    if not args or args[0] not in ["view", "set"]:
        await context.send(
            "Usage: `@BotName config <view|set> [key] [value]`", text_mode="styled"
        )
        return

    sub_command = args[0]

    if TYPE_CHECKING:
        assert isinstance(context.bot, SignalAIBot)

    if context.bot.persistence_manager is None:
        # This should not happen if the bot is initialized correctly.
        await context.send("⚠️ Error: Persistence manager not initialized.")
        return

    persistence_manager = context.bot.persistence_manager
    chat_context = persistence_manager.load_context(context.message.source)

    if sub_command == "view":
        config_text = "⚙️ **Chat Configuration**\n\n```\n"
        config_text += f"mode: {chat_context.mode}\n"
        config_text += (
            "```\n\n_Use `@BotName config set <key> <value>` to make changes._"
        )
        await context.send(config_text, text_mode="styled")

    elif sub_command == "set":
        if len(args) < 3:
            await context.send(
                "Usage: `@BotName config set <key> <value>`", text_mode="styled"
            )
            return

        key, value_str = args[1], " ".join(args[2:])

        if not hasattr(chat_context, key):
            await context.send(
                f"⚠️ Error: Unknown configuration key '{key}'", text_mode="styled"
            )
            return

        # Get the original type of the attribute to cast the new value
        original_type = type(getattr(chat_context, key))
        try:
            if original_type is bool:
                new_value = value_str.lower() == "true"
            else:
                new_value = original_type(value_str)
        except (ValueError, TypeError):
            await context.send(
                f"⚠️ Error: Invalid value type for '{key}'. Expected {original_type.__name__}.",
                text_mode="styled",
            )
            return

        setattr(chat_context, key, new_value)
        persistence_manager.save_context(chat_context)
        await context.send(
            f"✅ **Configuration updated:** `{key}` set to `{new_value}`",
            text_mode="styled",
        )
