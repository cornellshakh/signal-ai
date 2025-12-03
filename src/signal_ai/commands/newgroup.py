from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.groups import CreateGroupRequest
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler, CommandOptions
from .utils import safe_api_call


def build_new_group_command(options: CommandOptions) -> CommandHandler:
    @command("!newgroup")
    async def create_group(ctx: Context) -> None:
        if not options.secondary_member or options.secondary_member == ctx.settings.phone_number:
            await ctx.reply(
                SendMessageRequest(
                    message="single-number mode: skipping group creation; set SECONDARY_MEMBER to enable.",
                    recipients=[],
                )
            )
            return

        members = [ctx.message.source, options.secondary_member]
        request = CreateGroupRequest(name="signal-ai validation", members=members)  # type: ignore[list-item]
        result = await safe_api_call(
            ctx,
            "newgroup",
            ctx.groups.create_group(ctx.settings.phone_number, request),
        )
        if result is None:
            return
        group_id = result.get("id") or result.get("groupId") or "<unknown>"
        await ctx.reply(
            SendMessageRequest(
                message=f"created group: {group_id}",
                recipients=[],
            )
        )

    return create_group
