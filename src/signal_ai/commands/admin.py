from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler, CommandOptions


def build_admin_command(options: CommandOptions) -> CommandHandler:
    @command(
        "!admin",
        whitelisted=[options.admin_number] if options.admin_number else None,
        case_sensitive=True,
    )
    async def admin_only(ctx: Context) -> None:
        await ctx.reply(
            SendMessageRequest(
                message="admin path hit; whitelist respected",
                recipients=[],
            )
        )

    return admin_only
