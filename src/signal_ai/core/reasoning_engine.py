import structlog
from google.generativeai.types import FunctionDeclaration, ContentDict

from signal_ai.infrastructure.ai import AIClient
from .tool_manager import ToolManager
from .context import AppContext

log = structlog.get_logger()


class ReasoningEngine:
    """
    The reasoning engine, decoupled from the SignalBot library.
    """

    def __init__(
        self,
        ai_client: AIClient,
        tool_manager: ToolManager,
        persistence_manager,
        prompt_manager,
    ):
        self.ai_client = ai_client
        self.tool_manager = tool_manager
        self.persistence_manager = persistence_manager
        self.prompt_manager = prompt_manager

    async def handle_message(self, context: AppContext):
        """
        Handles an incoming message using the reasoning loop.
        """
        response = await self.execute(context)
        if response:
            await context.reply(response)

    async def execute(self, context: AppContext) -> str:
        """
        Executes the reasoning loop to generate a response.
        """
        history = context.persistent_context.history
        tool_schemas = self.tool_manager.get_tool_schemas()

        # Add user's message to history
        history.append({"role": "user", "parts": [context.message_text]})

        response = await self.ai_client.generate_response_with_tools(
            context.chat_id,
            context.message_text,
            [ContentDict(**h) for h in history],
            [FunctionDeclaration(**s) for s in tool_schemas],
        )

        if response.candidates[0].content.parts[0].function_call:
            # Handle tool call
            function_call = response.candidates[0].content.parts[0].function_call
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}
            tool_result = await self.tool_manager.dispatch(
                tool_name, context, **tool_args
            )

            # Add tool response to history
            history.append(
                {
                    "role": "model",
                    "parts": [
                        {
                            "function_call": {
                                "name": tool_name,
                                "args": tool_args,
                            }
                        }
                    ],
                }
            )
            history.append(
                {
                    "role": "tool",
                    "parts": [{"function_response": {"name": tool_name, "response": tool_result}}],
                }
            )

            # Get final response from AI
            final_response = await self.ai_client.generate_response(
                context.chat_id, "", [ContentDict(**h) for h in history]
            )
            history.append({"role": "model", "parts": [final_response]})
            await self.persistence_manager.save_context(context.chat_id)
            return final_response

        else:
            # Handle text response
            text_response = response.candidates[0].content.parts[0].text
            history.append({"role": "model", "parts": [text_response]})
            await self.persistence_manager.save_context(context.chat_id)
            return text_response