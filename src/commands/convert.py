import logging
import shlex
import subprocess
from signalbot import Command
from markitdown import MarkItDown
from pathlib import Path

log = logging.getLogger(__name__)

from signalbot import Command, Context, regex_triggered

class ConvertCommand(Command):
    """A command to convert an attached file or message text to Markdown using MarkItDown.
    To use this command, send the bot a message with a file attached or text to convert.
    """

    @regex_triggered(r"^!convert( .*)?$")
    async def handle(self, c: Context) -> None:
        """Convert the attached file or message text to Markdown"""
        log.info("ConvertCommand called")
        log.info(f"Message: {c.message.text}")
        log.info(f"Attachments: {c.message.attachments_local_filenames}")

        source_to_convert = None
        
        # Prioritize text/URL argument after the command
        message_text = c.message.text.split(' ', 1)[1] if len(c.message.text.split()) > 1 else None
        if message_text:
            source_to_convert = message_text
        # If no text argument, check for an attachment
        elif c.message.attachments_local_filenames:
            attachment_filename = c.message.attachments_local_filenames[0]
            source_to_convert = Path("/home/.local/share/signal-cli/attachments") / attachment_filename

        if source_to_convert:
            try:
                md = MarkItDown()
                result = md.convert(source_to_convert)
                markdown_content = result.text_content
                await c.send(markdown_content)
            except Exception as e:
                log.exception(f"Error converting: {e}")
                await c.send(f"Error converting: {e}")
        else:
            await c.send("Please provide a file, URL, or text to convert after the !convert command.")
