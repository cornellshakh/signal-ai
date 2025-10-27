import os
from signalbot import Context


async def help_command_handler(context: Context, args: list[str]):
    """
    Handles the 'help' command.
    """
    bot_name = os.environ.get("BOT_NAME", "BotName")

    help_text = f"""
🤖 **Signal AI Assistant**

> I'm a bot designed to assist you. Interact with me by mentioning my name (`@{bot_name}`) followed by a command or a question.

**Available Commands:**

```
┌
├─ 📋 todo      - Manage a shared to-do list.
├─ ⏰ remind    - Set a reminder.
├─ ⚙️ config    - Configure my settings for this chat.
├─ 🔎 search    - Search the web or summarize a URL.
└─ 🖼️ image     - Generate an image from a prompt.
```

_For more details, type `@{bot_name} help <command>`._
"""
    await context.send(help_text, text_mode="styled")
