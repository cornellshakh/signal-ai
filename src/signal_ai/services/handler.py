import asyncio
import json
from typing import Any

import structlog

from signal_ai.core.config import Settings
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.reasoning import ReasoningEngine
from signal_ai.services.state import StateManager

log = structlog.get_logger()


class MessageHandler:
    def __init__(
        self,
        reasoning_engine: ReasoningEngine,
        state_manager: StateManager,
        signal_transport: SignalTransport,
        config: Settings,
    ):
        self._reasoning_engine = reasoning_engine
        self._state_manager = state_manager
        self._signal_transport = signal_transport
        self._config = config
        self._processed_timestamps = set()

    async def start(self) -> None:
        """Listen for incoming messages and process them."""
        async for raw_message in self._signal_transport.listen():
            try:
                message = self._parse_message(raw_message)
                if message:
                    log.info("Passing message to reasoning engine.", message=message)
                    await self._reasoning_engine.process(message)
            except (json.JSONDecodeError, KeyError) as e:
                log.error("Failed to parse message", error=e, raw_message=raw_message)
            except BaseException as e:
                log.error("Unhandled exception in message handler", error=e, exc_info=True)

    async def stop(self) -> None:
        await self._signal_transport.close()

    def _parse_message(self, raw_message_str: str) -> dict[str, Any] | None:
        data = json.loads(raw_message_str)
        envelope = data.get("envelope", {})
        source = envelope.get("source")

        # Process incoming data messages from other users
        if "dataMessage" in envelope:
            message_content = envelope["dataMessage"]
            timestamp = message_content.get("timestamp")
            if timestamp in self._processed_timestamps:
                self._processed_timestamps.remove(timestamp)
                return None

            log.info(
                "Processing incoming data message.",
                source=source,
                message=message_content.get("message"),
            )
            return {
                "source": source,
                "text": message_content.get("message"),
                "timestamp": timestamp,
            }

        # Process "Note to Self" messages
        if "syncMessage" in envelope:
            sent_message = envelope.get("syncMessage", {}).get("sentMessage")
            if sent_message:
                destination = sent_message.get("destination")
                if (
                    source == self._config.signal_phone_number
                    and destination == self._config.signal_phone_number
                ):
                    timestamp = sent_message.get("timestamp")
                    self._processed_timestamps.add(timestamp)
                    log.info(
                        "Processing 'Note to Self' message.",
                        message=sent_message.get("message"),
                    )
                    message_text = sent_message.get("message")
                    if self._state_manager.is_self_sent_message(message_text):
                        log.info("Ignoring self-sent message.", message=message_text)
                        return None
                    return {
                        "source": source,
                        "text": message_text,
                        "timestamp": timestamp,
                    }

        log.info("Ignoring irrelevant message.", source=source)
        return None