import os
import json
from asyncio import Queue
import structlog
from pathlib import Path
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from signalbot import SignalBot, Message, Context
from signalbot.api import ReceiveMessagesError
from signalbot.bot import SignalBotError

from .core.persistence import PersistenceManager
from .core.message_handler import MessageHandler
from .core.ai_client import AIClient
from .core.logging import configure_logging
from .core.dispatcher import CommandDispatcher
from .core.group_manager import GroupManager
from .core.prompt_manager import PromptManager
from . import commands


log = structlog.get_logger()


class SignalAIBot(SignalBot):
    """
    Custom bot class to hold the persistence manager and scheduler,
    and to gracefully handle unknown message types.
    """

    _queue: Queue
    _running: bool
    _signal: Any

    def __init__(self, config):
        super().__init__(config)
        self.persistence_manager: Optional[PersistenceManager] = None
        self.scheduler: Optional[BackgroundScheduler] = None
        self.ai_client: Optional[AIClient] = None
        self.dispatcher: Optional[CommandDispatcher] = None
        self.message_handler: Optional[MessageHandler] = None
        self.group_manager: Optional[GroupManager] = None
        self.prompt_manager: Optional[PromptManager] = None

    async def _produce(self, name: int) -> None:
        """
        Overridden to handle KeyError when parsing messages.
        """
        log.info("producer.started", producer_name=name)
        try:
            async for raw_message in self._signal.receive():
                log.debug("message.received.raw", raw_message=raw_message)

                try:
                    # Attempt to parse the raw message as JSON to inspect its contents
                    parsed_message = json.loads(raw_message)
                    envelope = parsed_message.get("envelope", {})

                    # Filter out non-essential message types that don't contain user content
                    if "receiptMessage" in envelope or "typingMessage" in envelope:
                        log.info(
                            "message.filtered",
                            reason="Receipt or typing message",
                            filtered_message=parsed_message,
                        )
                        continue

                    # Handle sync messages intelligently to distinguish echoes from new messages
                    if "syncMessage" in envelope:
                        sync_message_data = envelope.get("syncMessage", {})

                        if "readMessages" in sync_message_data:
                            log.info(
                                "message.filtered",
                                reason="Read receipt sync message",
                                filtered_message=parsed_message,
                            )
                            continue

                        if "sentMessage" in sync_message_data:
                            sent_message = sync_message_data.get("sentMessage", {})
                            destination = sent_message.get("destination")

                            # If the destination is not the bot's own number, it's an echo of a message
                            # sent to another user. We must ignore it to prevent loops.
                            if destination and destination != self.config["phone_number"]:
                                log.info(
                                    "message.filtered",
                                    reason="Echo of an outgoing message to another user",
                                    filtered_message=parsed_message,
                                )
                                continue
                            # If the destination is the bot's own number, it's a "note to self" and should be processed.
                        # Note: Incoming messages from a user's linked device (like "note to self")
                        # can also arrive as a syncMessage with a 'dataMessage', so they are NOT filtered here.

                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, it's unlikely to be a message we want to process
                    log.warning(
                        "message.filter.failed",
                        reason="Non-JSON message",
                        raw_message=raw_message,
                    )
                    continue

                try:
                    message = await Message.parse(self._signal, raw_message)
                except Exception:
                    try:
                        # Try to parse the raw message as JSON for structured logging
                        parsed_message = json.loads(raw_message)
                        log.warning(
                            "message.parse.failed", parsed_message=parsed_message
                        )
                    except (json.JSONDecodeError, TypeError):
                        # Fallback for non-JSON or already-decoded messages
                        log.warning(
                            "message.parse.failed",
                            reason="unparseable",
                            raw_message=raw_message,
                        )
                    continue

                # Update groups if message is from an unknown group
                if (
                    message.is_group()
                    and message.group is not None
                    and self._groups_by_internal_id.get(message.group) is None
                ):
                    await self._detect_groups()

                if self.message_handler:
                    context = Context(self, message)
                    await self.message_handler.handle(context)

        except ReceiveMessagesError as e:
            raise SignalBotError(f"Cannot receive messages: {e}") from e

    async def _produce_consume_messages(
        self,
        producers: int = 1,
        consumers: int = 1,
    ) -> None:
        """
        Overridden to set the number of consumers to 1.
        """
        return await super()._produce_consume_messages(
            producers=producers, consumers=consumers
        )


def main() -> None:
    """Main function to run the bot."""
    try:
        configure_logging()
        signal_service = os.environ.get("SIGNAL_SERVICE")
        phone_number = os.environ.get("PHONE_NUMBER")

        log.info("bot.configured.signal_service", signal_service=signal_service)
        log.info("bot.configured.phone_number", phone_number=phone_number)

        config = {
            "signal_service": signal_service,
            "phone_number": phone_number,
            "download_attachments": True,
        }
        bot = SignalAIBot(config)

        # Initialize and attach PersistenceManager
        db_path = Path.home() / ".signal-ai" / "db.json"
        bot.persistence_manager = PersistenceManager(db_path)

        # Initialize and attach PromptManager
        bot.prompt_manager = PromptManager()

        # Initialize and attach AIClient
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key and bot.prompt_manager:
            bot.ai_client = AIClient(api_key, prompt_manager=bot.prompt_manager)

        # Initialize and attach CommandDispatcher and MessageHandler
        bot.dispatcher = CommandDispatcher(commands)
        bot.message_handler = MessageHandler(bot.dispatcher)
        bot.group_manager = GroupManager(bot)

        # Initialize and attach scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(bot.persistence_manager.backup_database, "interval", hours=1)
        # Placeholder for summarization service
        # scheduler.add_job(summarization_service, "interval", hours=6)
        bot.scheduler = scheduler

        bot.start()

    except Exception as e:
        log.error("bot.error", error=str(e))


if __name__ == "__main__":
    main()
