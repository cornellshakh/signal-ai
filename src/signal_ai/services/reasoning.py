import structlog

from signal_ai.domain.context import AppContext
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager
from signal_ai.services.tooling import ToolingService

log = structlog.get_logger()


class ReasoningEngine:
    def __init__(
        self,
        tooling_service: ToolingService,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
    ):
        self._tooling_service = tooling_service
        self._state_manager = state_manager
        self._ai_client = ai_client
        self._signal_transport = signal_transport

    async def process(self, message: dict) -> None:
        """
        Processes an incoming message, executes the appropriate tool, and sends a response.
        """
        text = message.get("text", "").strip()
        if not text or not text.startswith("!"):
            await self._handle_ai_mode(message)
            return

        parts = text[1:].split()
        if not parts:
            log.warning("Empty command received.")
            return

        command_name, *args = parts
        tool = self._tooling_service.tools.get(command_name)

        if not tool:
            log.warning("Command not found.", command=command_name)
            return

        context = await self._state_manager.load_context(message["source"])
        context.message = message
        try:
            response = await tool.execute(
                context,
                self._state_manager,
                self._ai_client,
                self._signal_transport,
                *args,
            )
            if response:
                await self._signal_transport.send(
                    {
                        "message": response,
                        "number": self._signal_transport._config.signal_phone_number,
                        "recipient": message["source"],
                    }
                )
        except Exception as e:
            log.error("Error executing tool.", tool=tool.name, error=e)

    def _create_context(self, message: dict) -> AppContext:
        """Creates an application context from an incoming message."""
        chat_id = message["source"]
        return AppContext(
            chat_id=chat_id,
            message=message,
        )

    async def _handle_ai_mode(self, message: dict) -> None:
        """Handles messages in AI mode."""
        log.info("Handling AI mode.", message=message)
        log.info("Loading context.", chat_id=message["source"])
        context = await self._state_manager.load_context(message["source"])
        log.info("Context loaded.", chat_id=context.chat_id)
        log.info("Generating AI response.", chat_id=context.chat_id)
        response = await self._ai_client.generate_response(
            chat_id=context.chat_id,
            prompt=message.get("text", ""),
            history=context.chat_history,
        )
        log.info("AI response received.", response=response)
        if response:
            context.chat_history.append({"role": "user", "parts": [message.get("text", "")]})
            context.chat_history.append({"role": "model", "parts": [response]})
            await self._state_manager.save_context(context)
            if message["source"] == self._signal_transport._config.signal_phone_number:
                self._state_manager.add_self_sent_message(response)
            await self._signal_transport.send(
                {
                    "message": response,
                    "number": self._signal_transport._config.signal_phone_number,
                    "recipient": message["source"],
                }
            )
        else:
            log.warning("AI returned an empty response.")
            await self._signal_transport.send(
                {
                    "message": "Sorry, I don't have a response for that.",
                    "number": self._signal_transport._config.signal_phone_number,
                    "recipient": message["source"],
                }
            )