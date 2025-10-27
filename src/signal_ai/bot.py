import logging
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from signalbot import SignalBot

from .core.persistence import PersistenceManager
from .commands.dispatcher import CommandDispatcher


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
        bot = SignalBot(config)

        # Register the unified command handler
        bot.register(CommandDispatcher())

        # Initialize PersistenceManager
        db_path = Path.home() / ".signal-ai" / "db.json"
        persistence_manager = PersistenceManager(db_path)

        # Schedule hourly backups
        scheduler = BackgroundScheduler()
        scheduler.add_job(persistence_manager.backup_database, "interval", hours=1)
        scheduler.start()

        bot.start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
