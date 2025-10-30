from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class TodoCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "todo"

    @property
    def description(self) -> str:
        return "Manages the to-do list for this chat."

    def help(self) -> str:
        return (
            "Usage: `!todo [add|list|done|clear|remove] [args...]`\n\n"
            "Manages the to-do list for this chat.\n\n"
            "**Subcommands:**\n"
            "- `add [item]`: Add an item to the to-do list.\n"
            "- `list`: Show the to-do list.\n"
            "- `done [index]`: Mark an item as done.\n"
            "- `clear`: Clear the to-do list.\n"
            "- `remove [index]`: Remove an item by its index."
        )

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.persistence_manager:
            return ErrorResult("Persistence manager not available.")

        if not args:
            sub_command = "list"
            text = None
        else:
            sub_command = args[0]
            text = " ".join(args[1:]) if len(args) > 1 else None

        chat_context = await bot.persistence_manager.load_context(c.chat_id)

        if sub_command == "add":
            if not text:
                return ErrorResult("Usage: `!todo add [item]`")
            chat_context.todos.append(text)
            await bot.persistence_manager.save_context(c.chat_id)
            return TextResult(f"Added to-do: `{text}`")

        elif sub_command == "list":
            if not chat_context.todos:
                return TextResult("No to-do items.")

            todo_list = ""
            for i, item in enumerate(chat_context.todos):
                todo_list += f"{i+1}. {item}\n"
            return TextResult(todo_list)

        elif sub_command == "done" or sub_command == "remove":
            if not text:
                return ErrorResult(f"Usage: `!todo {sub_command} [index]`")
            try:
                index = int(text) - 1
                if 0 <= index < len(chat_context.todos):
                    item = chat_context.todos.pop(index)
                    await bot.persistence_manager.save_context(c.chat_id)
                    if sub_command == "done":
                        return TextResult(f"Completed to-do: `{item}`")
                    else:
                        return TextResult(f"Removed to-do: `{item}`")
                else:
                    return ErrorResult("Invalid to-do index.")
            except ValueError:
                return ErrorResult("Invalid to-do index.")
        elif sub_command == "clear":
            chat_context.todos.clear()
            await bot.persistence_manager.save_context(c.chat_id)
            return TextResult("To-do list cleared.")
        else:
            return ErrorResult(f"Unknown subcommand: `{sub_command}`.")