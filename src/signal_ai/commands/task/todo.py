from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.persistence import PersistenceManager


class TaskCommand(Command):
    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager

    def describe(self) -> str:
        return "Manages the to-do list for this chat."

    def help(self) -> str:
        return (
            "Usage: `!task [add|list|done] [args...]`\n\n"
            "Manages the to-do list for this chat.\n\n"
            "**Subcommands:**\n"
            "- `add [item]`: Add an item to the to-do list.\n"
            "- `list`: Show the to-do list.\n"
            "- `done [index]`: Mark an item as done."
        )

    @regex_triggered(r"^!task(?: (add|list|done)(?: (.+))?)?$")
    async def handle(
        self, c: Context, sub_command: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        if not sub_command:
            await c.reply("Usage: `!task [add|list|done] [args...]`", text_mode="styled")
            return

        chat_context = self._persistence_manager.load_context(c.message.source)

        if sub_command == "add":
            if not value:
                await c.reply("Usage: `!task add [item]`", text_mode="styled")
                return
            chat_context.todos.append(value)
            self._persistence_manager.save_context(c.message.source)
            await c.reply(f"Added to-do: `{value}`", text_mode="styled")

        elif sub_command == "list":
            if not chat_context.todos:
                await c.reply("No to-do items.", text_mode="styled")
                return

            todo_list = ""
            for i, item in enumerate(chat_context.todos):
                todo_list += f"{i+1}. {item}\n"
            await c.reply(todo_list, text_mode="styled")

        elif sub_command == "done":
            if not value:
                await c.reply("Usage: `!task done [index]`", text_mode="styled")
                return
            try:
                index = int(value) - 1
                if 0 <= index < len(chat_context.todos):
                    item = chat_context.todos.pop(index)
                    self._persistence_manager.save_context(c.message.source)
                    await c.reply(f"Completed to-do: `{item}`", text_mode="styled")
                else:
                    await c.reply("Invalid to-do index.", text_mode="styled")
            except ValueError:
                await c.reply("Invalid to-do index.", text_mode="styled")
