import logging
import os

from example.attachments import AttachmentCommand
from example.delete import DeleteCommand
from example.delete import DeleteCommand as ReceiveDeleteCommand
from example.edit import EditCommand
from example.multiple_triggered import TriggeredCommand
from example.ping import PingCommand
from example.regex_triggered import RegexTriggeredCommand
from example.reply import ReplyCommand
from example.styles import StylesCommand
from signalbot import SignalBot

from .commands.convert import ConvertCommand
from .commands.hello import HelloCommand
from .commands.help import HelpCommand
from .commands.search_web import SearchWebCommand


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
            level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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

        # enable a chat command for all contacts and all groups
        bot.register(PingCommand())
        bot.register(ReplyCommand())

        # enable a chat command only for groups
        bot.register(AttachmentCommand())

        # enable a chat command for one specific group with the name "My Group"

        # chat command is enabled for all groups and one specific contact
        bot.register(TriggeredCommand())

        bot.register(RegexTriggeredCommand())

        bot.register(EditCommand())
        bot.register(DeleteCommand())
        bot.register(ReceiveDeleteCommand())
        bot.register(StylesCommand())
        bot.register(SearchWebCommand())
        bot.register(ConvertCommand())
        bot.register(HelloCommand())
        bot.register(HelpCommand())

        bot.start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
