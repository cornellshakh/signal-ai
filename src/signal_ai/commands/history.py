from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler


def build_history_command() -> CommandHandler:
    @command("!history")
    async def recent_messages(ctx: Context) -> None:
        pretty = (
            "history is not available via signal-cli-rest-api; "
            "persist the websocket stream if you need archives."
        )
        await ctx.reply(
            SendMessageRequest(
                message=f"recent messages:\n{pretty}",
                recipients=[],
            )
        )

    return recent_messages
