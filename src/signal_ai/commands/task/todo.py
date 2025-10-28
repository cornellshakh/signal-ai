from typing import List, cast
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
            "Usage: `!task [add|list|done] [args...]`\n\n"
            "Manages the to-do list for this chat.\n\n"
            "**Subcommands:**\n"
            "- `add [item]`: Add an item to the to-do list.\n"
            "- `list`: Show the to-do list.\n"
            "- `done [index]`: Mark an item as done."
        )

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        persistence_manager = bot.persistence_manager
        if not persistence_manager:
            await c.reply("Persistence manager not available.")
            return

        if not args:
            await c.reply("Usage: `!task [add|list|done] [args...]`", text_mode="styled")
            return

        sub_command = args[0]
        chat_context = persistence_manager.load_context(c.message.source)

        if sub_command == "add":
            if len(args) < 2:
                await c.reply("Usage: `!task add [item]`", text_mode="styled")
                return
            value = " ".join(args[1:])
            chat_context.todos.append(value)
            persistence_manager.save_context(c.message.source)
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
            if len(args) < 2:
                await c.reply("Usage: `!task done [index]`", text_mode="styled")
                return
            try:
                index = int(args[1]) - 1
                if 0 <= index < len(chat_context.todos):
                    item = chat_context.todos.pop(index)
                    persistence_manager.save_context(c.message.source)
                    await c.reply(f"Completed to-do: `{item}`", text_mode="styled")
                else:
                    await c.reply("Invalid to-do index.", text_mode="styled")
            except ValueError:
                await c.reply("Invalid to-do index.", text_mode="styled")
        else:
            await c.reply(f"Unknown subcommand: `{sub_command}`.", text_mode="styled")
