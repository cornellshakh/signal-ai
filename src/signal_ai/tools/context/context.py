import re
from typing import Any, Optional

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.prompt import PromptManager
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class ContextSchema(BaseModel):
    sub_command: str = Field(
        "view", description="The subcommand to run (view, clear, new)."
    )
    text: Optional[str] = Field(None, description="The text to use.")
    num_messages: int = Field(10, description="The number of messages to view.")


class ContextTool(BaseTool):
    """
    Manages the chat context.
    """

    name = "context"
    description = "Manages the chat context."
    schema = ContextSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        prompt_manager: PromptManager,
        sub_command: str = "view",
        text: Optional[str] = None,
        num_messages: int = 10,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if sub_command == "view":
            history = context.chat_history
            if not history:
                return "Chat history is empty."

            start_index = max(0, len(history) - num_messages)
            formatted_history = []
            for i, item in enumerate(history[start_index:], start=start_index + 1):
                role = item.get("role", "unknown").capitalize()
                parts = item.get("parts", [])
                content = parts[0] if parts else ""
                formatted_history.append(f"_{i}_. *{role}*:\n{content}")

            return "\n\n".join(formatted_history)

        elif sub_command == "clear":
            context.chat_history = []
            await state_manager.save_context(context)
            await ai_client.clear_chat_session(context.chat_id)
            return "Chat history and AI session cache have been cleared."

        elif sub_command == "new":
            if not text:
                return "Usage: `!context new <prompt>`"

            try:
                group_name_prompt = prompt_manager.get(
                    "generate_group_name", prompt=text
                )
                group_name = await ai_client.generate_response(
                    chat_id=context.chat_id, prompt=group_name_prompt, history=[]
                )
                group_name = re.sub(r"[*_~`[\]()]", "", group_name.strip().strip('"'))

                # The logic for creating a group and adding the user would go here.
                # This is a placeholder for now.
                return f"I've created the group '**{group_name}**' and added you to it."

            except Exception as e:
                return f"An error occurred: {e}"

        else:
            return f"Unknown subcommand: `{sub_command}`."