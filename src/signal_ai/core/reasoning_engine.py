import structlog
import json
from typing import Dict, Any, List, cast, Optional
from google.generativeai.types import ContentDict, FunctionDeclaration
from google.generativeai.protos import FunctionCall

from .ai_client import AIClient
from .tool_manager import ToolManager
from signalbot import Context

log = structlog.get_logger()


class CapturingContext(Context):
    """A proxy context to capture replies instead of sending them."""

    def __init__(self, bot, message):
        super().__init__(bot, message)
        self.captured_reply = None

    async def reply(self, text: str, **kwargs):
        self.captured_reply = text
        log.info("context.capture_reply", reply=text)


class ReasoningEngine:
    """
    Manages the thought-action-observation cycle for complex, multi-step tasks.
    """

    def __init__(self, ai_client: AIClient, tool_manager: ToolManager):
        """
        Initializes the ReasoningEngine.

        Args:
            ai_client: The AI client for making LLM calls.
            tool_manager: The tool manager for executing tools.
        """
        self.ai_client = ai_client
        self.tool_manager = tool_manager

    async def execute(
        self,
        c: Context,
        prompt: str,
        history: List[Dict[str, Any]],
        max_steps: int = 10,
    ) -> Optional[str]:
        """
        Executes the reasoning loop to accomplish a task.

        Args:
            c: The original message context.
            prompt: The user's prompt.
            history: The conversation history.
            max_steps: The maximum number of steps to take.

        Returns:
            The final response to the user.
        """
        log.info("reasoning_engine.execute.start", prompt=prompt, max_steps=max_steps)

        current_prompt = prompt
        for i in range(max_steps):
            log.info("reasoning_engine.step", step=i + 1)

            # 1. Thought: Call the AI to decide the next action.
            tool_schemas: List[FunctionDeclaration] = self.tool_manager.get_tool_schemas()
            response = await self.ai_client.generate_response_with_tools(
                chat_id=c.message.source,
                prompt=current_prompt,
                history=cast(List[ContentDict], history),
                tool_schemas=tool_schemas,
            )
            # On subsequent iterations, the prompt is empty, and the AI relies on history.
            current_prompt = ""

            # The response object is an AsyncGenerationResponse, not a string.
            # We need to check for tool calls within its structure.
            if not response.candidates:
                # No candidates, so we're done.
                log.info("reasoning_engine.execute.done", response=None)
                return None
            candidate = response.candidates[0]
            if not candidate.content.parts or not candidate.content.parts[0].function_call:
                # No tool call, so we're done.
                final_response = ""
                for part in candidate.content.parts:
                    final_response += part.text
                log.info("reasoning_engine.execute.done", response=final_response)
                return final_response

            # 2. Action: Execute the chosen tool(s).
            tool_call: FunctionCall = candidate.content.parts[0].function_call
            tool_name = tool_call.name
            tool_args = dict(tool_call.args)

            log.info(
                "reasoning_engine.action", tool_name=tool_name, tool_args=tool_args
            )

            tool = self.tool_manager.tools.get(tool_name)
            if not tool:
                observation = f"Unknown tool: {tool_name}"
            else:
                try:
                    capturing_context = CapturingContext(c.bot, c.message)
                    if tool.ArgsSchema:
                        await tool.handle(capturing_context, tool_args)
                    else:
                        await tool.handle(capturing_context)  # No args to pass
                    observation = capturing_context.captured_reply
                    if observation is None:
                        observation = (
                            f"Tool {tool_name} executed successfully with no output."
                        )
                except Exception as e:
                    log.error("reasoning_engine.tool.error", error=e, exc_info=True)
                    observation = f"Error executing tool {tool_name}: {e}"

            # 3. Observation: Feed the result back to the AI.
            log.info("reasoning_engine.observation", observation=observation)
            
            # Append the AI's tool call to history
            history.append(
                {
                    "role": "model", # Use 'model' for Gemini's role
                    "parts": [
                        {"function_call": {"name": tool_name, "args": tool_args}}
                    ],
                }
            )
            # Append the tool's result to history
            history.append(
                {
                    "role": "user", # Use 'user' role for tool responses
                    "parts": [
                        {
                            "function_response": {
                                "name": tool_name,
                                "response": {"content": observation},
                            }
                        }
                    ],
                }
            )
            # The prompt for the next iteration is now handled by the history

        log.warning("reasoning_engine.max_steps_reached")
        return None
