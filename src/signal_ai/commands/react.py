from __future__ import annotations

import asyncio
import structlog

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.reactions import ReactionRequest
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler

log = structlog.get_logger()


async def _remove_own_reaction(ctx: Context, emoji: str) -> None:
    request = ReactionRequest(
        reaction=emoji,
        target_author=ctx.message.source,
        timestamp=ctx.message.timestamp,
        recipient=ctx.message.group["groupId"]
        if ctx.message.is_group() and ctx.message.group
        else ctx.message.source,
    )
    try:
        await ctx.reactions.remove_reaction(
            ctx.settings.phone_number,
            request.model_dump(by_alias=True, exclude_none=True),
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("command.react.remove_failed", error=str(exc))


def build_react_command() -> CommandHandler:
    @command("!react")
    async def react(ctx: Context) -> None:
        emoji = "👍"
        await ctx.react(emoji)
        await ctx.reply(
            SendMessageRequest(
                message="reacted; removing shortly",
                recipients=[],
            )
        )
        await asyncio.sleep(3)
        await _remove_own_reaction(ctx, emoji)

    return react
