from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler


def build_echo_command() -> CommandHandler:
    @command("!echo")
    async def echo(ctx: Context) -> None:
        await ctx.start_typing()
        try:
            payload = ctx.message.message or ""
            await ctx.reply(SendMessageRequest(message=f"echo: {payload}", recipients=[]))
        finally:
            await ctx.stop_typing()

    return echo
