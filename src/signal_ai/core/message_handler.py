import logging
import json
from signalbot import Message, SignalAPI


class MessageHandler:
    @staticmethod
    async def parse(signal: SignalAPI, raw_message: dict) -> Message | None:
        """
        Parses a raw message dictionary into a Message object.
        Handles potential parsing errors and logs them.
        """
        try:
            # The library expects a string, so we'll dump the dict to a JSON string
            return await Message.parse(signal, json.dumps(raw_message))
        except Exception as e:
            logging.error(f"Failed to parse message: {e}")
            logging.debug(f"Problematic raw message: {raw_message}")
            return None
