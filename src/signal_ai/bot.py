import logging
import os
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from signalbot import SignalBot

from .core.persistence import PersistenceManager
from .commands.dispatcher import CommandDispatcher


class SignalAIBot(SignalBot):
    """Custom bot class to hold the persistence manager and scheduler."""

    def __init__(self, config):
        super().__init__(config)
        self.persistence_manager: Optional[PersistenceManager] = None
        self.scheduler: Optional[BackgroundScheduler] = None


def main() -> None:
    """Main function to run the bot."""
    try:
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        try:
            log_level = getattr(logging, log_level_str)
        except AttributeError:
            logging.warning(f"Invalid log level: {log_level_str}, defaulting to INFO")
            log_level = logging.INFO

        # Configure logging for all modules
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        signal_service = os.environ.get("SIGNAL_SERVICE")
        phone_number = os.environ.get("PHONE_NUMBER")

        logging.info(f"Signal service: {signal_service}")
        logging.info(f"Phone number: {phone_number}")

        config = {
            "signal_service": signal_service,
            "phone_number": phone_number,
            "download_attachments": True,
        }
        bot = SignalAIBot(config)

        # Initialize and attach PersistenceManager
        db_path = Path.home() / ".signal-ai" / "db.json"
        bot.persistence_manager = PersistenceManager(db_path)

        # Register command handlers
        bot.register(CommandDispatcher())

        # Initialize and attach scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(bot.persistence_manager.backup_database, "interval", hours=1)
        bot.scheduler = scheduler

        bot.start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
