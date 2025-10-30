import logging
from pathlib import Path
from typing import Any, Optional, Union

from markitdown import MarkItDown

from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext

log = logging.getLogger(__name__)


class ConvertCommand(BaseCommand):
    """
    A command to convert an attached file or message text to Markdown using MarkItDown.
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

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        """Convert the attached file or message text to Markdown"""
        log.info("ConvertCommand called")

        source_to_convert = " ".join(args) if args else None

        if not source_to_convert and c.raw_context.message.attachments_local_filenames:
            attachment_filename = c.raw_context.message.attachments_local_filenames[0]
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
                return TextResult(markdown_content)
            except Exception as e:
                log.exception(f"Error converting: {e}")
                return ErrorResult(f"Error converting: {e}")
        else:
            return ErrorResult(
                "Please provide a file, URL, or text to convert after the !convert command."
            )