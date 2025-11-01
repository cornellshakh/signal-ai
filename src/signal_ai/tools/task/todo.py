from typing import Any, Optional

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class TodoSchema(BaseModel):
    sub_command: str = Field(
        "list", description="The subcommand to run (add, list, done, clear, remove)."
    )
    text: Optional[str] = Field(None, description="The text to use.")


class TodoTool(BaseTool):
    """
    Manages the to-do list for this chat.
    """

    name = "task"
    description = "Manages the to-do list for this chat."
    schema = TodoSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        *args: str,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if not args:
            sub_command = "list"
            text = None
        else:
            sub_command = args[0]
            text = " ".join(args[1:]) if len(args) > 1 else None

        if sub_command == "add":
            if not text:
                return "Usage: `!task add [item]`"
            context.todos.append(text)
            await state_manager.save_context(context)
            return f"Added to-do: `{text}`"

        elif sub_command == "list":
            if not context.todos:
                return "No to-do items."

            todo_list = ""
            for i, item in enumerate(context.todos):
                todo_list += f"{i+1}. {item}\n"
            return todo_list

        elif sub_command == "done" or sub_command == "remove":
            if not text:
                return f"Usage: `!task {sub_command} [index]`"
            try:
                index = int(text) - 1
                if 0 <= index < len(context.todos):
                    item = context.todos.pop(index)
                    await state_manager.save_context(context)
                    if sub_command == "done":
                        return f"Completed to-do: `{item}`"
                    else:
                        return f"Removed to-do: `{item}`"
                else:
                    return "Invalid to-do index."
            except ValueError:
                return "Invalid to-do index."
        elif sub_command == "clear":
            context.todos.clear()
            await state_manager.save_context(context)
            return "To-do list cleared."
        else:
            return f"Unknown subcommand: `{sub_command}`."