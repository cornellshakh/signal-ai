import os
from asyncio import Queue
import structlog
from pathlib import Path
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from signalbot import SignalBot, Message
from signalbot.api import ReceiveMessagesError
from signalbot.bot import SignalBotError
from signalbot.message import UnknownMessageFormatError

from .core.persistence import PersistenceManager
from .core.message_handler import MessageHandler
from .core.ai_client import AIClient
from .core.logging import configure_logging


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

    async def _produce(self, name: int) -> None:
        """
        Overridden to handle KeyError when parsing messages.
        """
        log.info("producer_started", producer_name=name)
        try:
            async for raw_message in self._signal.receive():
                log.debug("raw_message_received", raw_message=raw_message)

                try:
                    message = await Message.parse(self._signal, raw_message)
                except Exception:
                    log.warning("message_parse_error", raw_message=raw_message)
                    continue

                # Update groups if message is from an unknown group
                if (
                    message.is_group()
                    and message.group is not None
                    and self._groups_by_internal_id.get(message.group) is None
                ):
                    await self._detect_groups()

                await self._ask_commands_to_handle(message)

        except ReceiveMessagesError as e:
            raise SignalBotError(f"Cannot receive messages: {e}") from e


def main() -> None:
    """Main function to run the bot."""
    try:
        configure_logging()
        signal_service = os.environ.get("SIGNAL_SERVICE")
        phone_number = os.environ.get("PHONE_NUMBER")

        log.info("signal_service_configured", signal_service=signal_service)
        log.info("phone_number_configured", phone_number=phone_number)

        config = {
            "signal_service": signal_service,
            "phone_number": phone_number,
            "download_attachments": True,
        }
        bot = SignalAIBot(config)

        # Initialize and attach PersistenceManager
        db_path = Path.home() / ".signal-ai" / "db.json"
        bot.persistence_manager = PersistenceManager(db_path)

        # Initialize and attach AIClient
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            bot.ai_client = AIClient(api_key)

        # Register command handlers
        bot.register(MessageHandler())

        # Initialize and attach scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(bot.persistence_manager.backup_database, "interval", hours=1)
        # Placeholder for summarization service
        # scheduler.add_job(summarization_service, "interval", hours=6)
        bot.scheduler = scheduler

        bot.start()

    except Exception as e:
        log.error("an_error_occurred", error=str(e))


if __name__ == "__main__":
    main()
