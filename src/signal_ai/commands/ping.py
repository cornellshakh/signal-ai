from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler


def build_ping_command() -> CommandHandler:
    @command("!ping")
    async def ping(ctx: Context) -> None:
        await ctx.reply(SendMessageRequest(message="pong", recipients=[]))

    return ping
