from typing import cast, Dict, Any, Optional
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class TaskCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "task"

    @property
    def description(self) -> str:
        return "Manages the to-do list for this chat."

    def help(self) -> str:
        return (
            "Usage: `!task [add|list|done|clear|remove] [args...]`\n\n"
            "Manages the to-do list for this chat.\n\n"
            "**Subcommands:**\n"
            "- `add [item]`: Add an item to the to-do list.\n"
            "- `list`: Show the to-do list.\n"
            "- `done [index]`: Mark an item as done.\n"
            "- `clear`: Clear the to-do list.\n"
            "- `remove [index]`: Remove an item by its index."
        )

    @property
    def ArgsSchema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "sub_command": {
                    "type": "string",
                    "description": "The subcommand to execute (add, list, done, clear, or remove).",
                },
                "text": {
                    "type": "string",
                    "description": "The text of the to-do item or the index to mark as done.",
                },
            },
        }

    async def handle(self, c: Context, args: Dict[str, Any]) -> None:
        bot = cast("SignalAIBot", c.bot)
        persistence_manager = bot.persistence_manager
        if not persistence_manager:
            await c.reply("Persistence manager not available.")
            return

        sub_command = args.get("sub_command")
        text = args.get("text")
        chat_context = persistence_manager.load_context(c.message.source)

        if sub_command == "add":
            if not text:
                await c.reply("Usage: `!task add [item]`", text_mode="styled")
                return
            chat_context.todos.append(text)
            persistence_manager.save_context(c.message.source)
            await c.reply(f"Added to-do: `{text}`", text_mode="styled")

        elif sub_command == "list":
            if not chat_context.todos:
                await c.reply("No to-do items.", text_mode="styled")
                return

            todo_list = ""
            for i, item in enumerate(chat_context.todos):
                todo_list += f"{i+1}. {item}\n"
            await c.reply(todo_list, text_mode="styled")

        elif sub_command == "done" or sub_command == "remove":
            if not text:
                await c.reply(f"Usage: `!task {sub_command} [index]`", text_mode="styled")
                return
            try:
                index = int(text) - 1
                if 0 <= index < len(chat_context.todos):
                    item = chat_context.todos.pop(index)
                    persistence_manager.save_context(c.message.source)
                    if sub_command == "done":
                        await c.reply(f"Completed to-do: `{item}`", text_mode="styled")
                    else:
                        await c.reply(f"Removed to-do: `{item}`", text_mode="styled")
                else:
                    await c.reply("Invalid to-do index.", text_mode="styled")
            except ValueError:
                await c.reply("Invalid to-do index.", text_mode="styled")
        elif sub_command == "clear":
            chat_context.todos.clear()
            persistence_manager.save_context(c.message.source)
            await c.reply("To-do list cleared.", text_mode="styled")
        else:
            await c.reply(f"Unknown subcommand: `{sub_command}`.", text_mode="styled")
