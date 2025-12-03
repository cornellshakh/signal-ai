from __future__ import annotations

import base64

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.link_preview import LinkPreview
from signal_client.infrastructure.schemas.requests import (
    MessageMention,
    SendMessageRequest,
)

from .types import CommandHandler


def build_share_command() -> CommandHandler:
    @command("!share")
    async def share(ctx: Context) -> None:
        mention_text = ctx.message.source
        url = "https://example.com"
        message_text = (
            f"Attachment + mention of {mention_text} + preview link: {url}"
        )
        mention_start = message_text.index(mention_text)
        payload = SendMessageRequest(
            message=message_text,
            recipients=[],
            base64_attachments=[base64.b64encode(b"signal-ai validation").decode()],
            mentions=[
                MessageMention(
                    author=mention_text, start=mention_start, length=len(mention_text)
                )
            ],
            link_preview=LinkPreview(
                url=url,
                title="Example preview",
                description="Preview emitted by signal-ai validator",
            ),
        )
        await ctx.send(payload)

    return share
