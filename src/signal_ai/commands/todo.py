from typing import TYPE_CHECKING
from signalbot import Context

if TYPE_CHECKING:
    from ..bot import SignalAIBot


async def todo_command_handler(context: Context, args: list[str]):
    """
    Handles the 'todo' command and its sub-commands.
    """
    if not args or args[0] not in ["add", "list", "done"]:
        await context.send(
            "Usage: `@BotName todo <add|list|done> [task|task_number]`",
            text_mode="styled",
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

    if sub_command == "add":
        if len(args) < 2:
            await context.send(
                "Usage: `@BotName todo add <task description>`", text_mode="styled"
            )
            return
        task = " ".join(args[1:])
        chat_context.todo_list.append(task)
        persistence_manager.save_context(chat_context)
        await context.send(
            f"✅ **Todo added:** `{len(chat_context.todo_list)}. {task}`",
            text_mode="styled",
        )

    elif sub_command == "list":
        if not chat_context.todo_list:
            await context.send("📋 Your to-do list is empty.", text_mode="styled")
            return

        todo_text = "📋 **To-Do List**\n\n"
        for i, task in enumerate(chat_context.todo_list, 1):
            todo_text += f"`{i}.` {task}\n"

        await context.send(todo_text, text_mode="styled")

    elif sub_command == "done":
        if len(args) < 2 or not args[1].isdigit():
            await context.send(
                "Usage: `@BotName todo done <task_number>`", text_mode="styled"
            )
            return

        task_number = int(args[1])
        if 1 <= task_number <= len(chat_context.todo_list):
            removed_task = chat_context.todo_list.pop(task_number - 1)
            persistence_manager.save_context(chat_context)
            await context.send(
                f"✅ **Completed:** `{removed_task}`", text_mode="styled"
            )
        else:
            await context.send(
                f"⚠️ Error: Invalid task number. You have {len(chat_context.todo_list)} items on your list.",
                text_mode="styled",
            )
