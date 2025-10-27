from signalbot import Context
from ..core.persistence import PersistenceManager


async def handle_config(
    c: Context, args: list[str], persistence_manager: PersistenceManager
):
    """
    Handles the !config command.
    """
    if not args:
        await c.reply("Usage: `!config [view|set] [args...]`")
        return

    sub_command = args[0].lower()
    chat_context = persistence_manager.load_context(c.message.source)

    if sub_command == "view":
        mode = chat_context.config.mode
        await c.reply(f"Current mode: `{mode}`")

    elif sub_command == "set":
        if len(args) < 2:
            await c.reply("Usage: `!config set mode [ai|quiet|parrot]`")
            return

        key = args[1].lower()
        if key == "mode":
            if len(args) < 3:
                await c.reply("Usage: `!config set mode [ai|quiet|parrot]`")
                return

            new_mode = args[2].lower()
            if new_mode in ["ai", "quiet", "parrot"]:
                chat_context.config.mode = new_mode
                persistence_manager.save_context(c.message.source)
                await c.reply(f"Mode set to `{new_mode}`.")
            else:
                await c.reply(
                    f"Invalid mode: `{new_mode}`. Must be one of `ai`, `quiet`, or `parrot`."
                )
        else:
            await c.reply(f"Unknown config key: `{key}`.")
    else:
        await c.reply(f"Unknown sub-command: `{sub_command}`. Use `view` or `set`.")
