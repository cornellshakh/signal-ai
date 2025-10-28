import logging
from pathlib import Path
from typing import Optional

from markitdown import MarkItDown
from signalbot import Command, Context, regex_triggered

log = logging.getLogger(__name__)


class ConvertCommand(Command):
    """
    A command to convert an attached file or message text to Markdown using MarkItDown.
    To use this command, send the bot a message with a file attached or text to convert.
    """

    @regex_triggered(r"^!utility convert(?: (.+))?$")
    async def handle(self, c: Context, source_to_convert: Optional[str] = None) -> None:
        """Convert the attached file or message text to Markdown"""
        log.info("ConvertCommand called")

        if not source_to_convert and c.message.attachments_local_filenames:
            attachment_filename = c.message.attachments_local_filenames[0]
            source_to_convert = (
                Path.home()
                / ".local/share/signal-cli/attachments"
                / attachment_filename
            )

        if source_to_convert:
            try:
                md = MarkItDown()
                result = md.convert(source_to_convert)
                markdown_content = result.text_content
                await c.send(markdown_content, text_mode="styled")
            except Exception as e:
                log.exception(f"Error converting: {e}")
                await c.send(f"Error converting: {e}", text_mode="styled")
        else:
            await c.send(
                "Please provide a file, URL, or text to convert after the !convert command.",
                text_mode="styled",
            )
