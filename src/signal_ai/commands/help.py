from signalbot import Context


async def handle_help(c: Context, args: list[str]):
    """
    Displays the help message.
    """
    # The bot_name is needed for the help message.
    # It's not available here directly, so we'll pass it in from the MessageHandler.
    # This is a temporary solution until a better command dispatcher is in place.
    bot_name = args[0]

    help_text = f"""
*Commands*
- `@{bot_name} !help`: Shows this help message.
- `@{bot_name} !config view`: Views the current chat configuration.
- `@{bot_name} !config set mode [ai|quiet|parrot]`: Sets the bot's interaction mode.
- `@{bot_name} !todo add [item]`: Adds an item to the to-do list.
- `@{bot_name} !todo list`: Lists all items in the to-do list.
- `@{bot_name} !todo done [index]`: Marks a to-do item as done.
- `@{bot_name} !remind [in|at] [time] [message]`: Sets a reminder.
- `@{bot_name} !search [query]`: Searches the web.
- `@{bot_name} !image [prompt]`: Generates an image.
"""
    await c.reply(help_text, text_mode="styled")
