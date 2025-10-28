from signalbot import Context
from ..core.persistence import PersistenceManager


async def handle_todo(
    c: Context, args: list[str], persistence_manager: PersistenceManager
):
    """
    Handles the !todo command.
    """
    if not args:
        await c.reply("Usage: `!todo [add|list|done] [args...]`", text_mode="styled")
        return

    sub_command = args[0].lower()
    chat_context = persistence_manager.load_context(c.message.source)

    if sub_command == "add":
        if len(args) < 2:
            await c.reply("Usage: `!todo add [item]`", text_mode="styled")
            return
        item = " ".join(args[1:])
        chat_context.todos.append(item)
        persistence_manager.save_context(c.message.source)
        await c.reply(f"Added to-do: `{item}`", text_mode="styled")

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
            await c.reply("Usage: `!todo done [index]`", text_mode="styled")
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
        await c.reply(
            f"Unknown sub-command: `{sub_command}`. Use `add`, `list`, or `done`.",
            text_mode="styled",
        )
