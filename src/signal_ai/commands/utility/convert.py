import logging
from pathlib import Path
from typing import List

from markitdown import MarkItDown
from signalbot import Context
from ...core.command import BaseCommand

log = logging.getLogger(__name__)


class ConvertCommand(BaseCommand):
    """
    A command to convert an attached file or message text to Markdown using MarkItDown.
    To use this command, send the bot a message with a file attached or text to convert.
    """

    @property
    def name(self) -> str:
        return "convert"

    @property
    def description(self) -> str:
        return "Converts a file, URL, or text to Markdown."

    def help(self) -> str:
        return (
            "Usage: `!convert [file|URL|text]`\n\n"
            "Converts a file, URL, or text to Markdown."
        )

    async def handle(self, c: Context, args: List[str]) -> None:
        """Convert the attached file or message text to Markdown"""
        log.info("ConvertCommand called")

        source_to_convert = " ".join(args) if args else None

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
                result = md.convert(str(source_to_convert))
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
