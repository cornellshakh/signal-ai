import logging  # noqa: INP001
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

load_dotenv()

from example.attachments import AttachmentCommand
from example.delete import DeleteCommand
from example.edit import EditCommand
from example.ping import PingCommand
from example.delete import DeleteCommand as ReceiveDeleteCommand
from example.regex_triggered import RegexTriggeredCommand
from example.reply import ReplyCommand
from example.styles import StylesCommand
from example.multiple_triggered import TriggeredCommand as TriggeredCommand
from example.typing import TypingCommand

from signalbot import SignalBot, enable_console_logging


def main() -> None:
    try:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        try:
            log_level = getattr(logging, log_level)
        except AttributeError:
            logging.warning(f"Invalid log level: {log_level}, defaulting to INFO")
            log_level = logging.INFO

        enable_console_logging(log_level)

        signal_service = os.environ.get("SIGNAL_SERVICE")
        phone_number = os.environ.get("PHONE_NUMBER")

        config = {
            "signal_service": signal_service,
            "phone_number": phone_number,
        }
        bot = SignalBot(config)

        # enable a chat command for all contacts and all groups
        bot.register(PingCommand())
        bot.register(ReplyCommand())

        # enable a chat command only for groups
        bot.register(AttachmentCommand(), contacts=False, groups=True)

        # enable a chat command for one specific group with the name "My Group"
        bot.register(TypingCommand(), groups=["My Group"])

        # chat command is enabled for all groups and one specific contact
        bot.register(TriggeredCommand(), contacts=["+490123456789"], groups=True)

        bot.register(RegexTriggeredCommand())

        bot.register(EditCommand())
        bot.register(DeleteCommand())
        bot.register(ReceiveDeleteCommand())
        bot.register(StylesCommand())
        bot.start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
