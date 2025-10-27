import logging
import shlex
import subprocess
from signalbot import Command
from markitdown import MarkItDown

log = logging.getLogger(__name__)

from signalbot import Command, Context, triggered

class ConvertCommand(Command):
    """A command to convert an attached file or message text to Markdown using MarkItDown.
    To use this command, send the bot a message with a file attached or text to convert.
    """

    @triggered("!convert")
    async def handle(self, c: Context) -> None:
        """Convert the attached file or message text to Markdown"""
        log.info("ConvertCommand called")
        log.info(f"Message: {c.message.text}")
        log.info(f"Attachments: {c.message.attachments_local_filenames}")

        if c.message.attachments_local_filenames:
            log.info("Converting attachment")
            attachment_filename = c.message.attachments_local_filenames[0]
            attachment_path = f"/home/user/.local/share/signal-api/attachments/{attachment_filename}"

            log.info(f"Attachment path: {attachment_path}")

            try:
                md = MarkItDown()
                result = md.convert(attachment_path)
                markdown_content = result.text_content
                await c.send(markdown_content)

            except Exception as e:
                log.exception(f"Error converting file: {e}")
                await c.send(f"Error converting file: {e}")

        elif c.message.text:
            log.info("Converting message text")
            message_text = c.message.text.split(' ', 1)[1] if len(c.message.text.split()) > 1 else None
            if message_text:
                try:
                    md = MarkItDown()
                    markdown_content = md.convert(message_text).text_content
                    await c.send(markdown_content)
                except Exception as e:
                    log.exception(f"Error converting text: {e}")
                    await c.send(f"Error converting text: {e}")
            else:
                await c.send("Please provide text to convert.")

        else:
            await c.send("Please attach a file or provide text to convert.")