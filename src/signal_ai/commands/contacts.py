from __future__ import annotations

from typing import Any

import aiohttp

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler, CommandOptions
from .utils import safe_api_call


async def _fetch_contacts(ctx: Context, base_url_override: str | None) -> list[dict[str, Any]]:
    if not base_url_override:
        return await ctx.contacts.get_contacts(ctx.settings.phone_number)

    url = f"{base_url_override.rstrip('/')}/v1/contacts/{ctx.settings.phone_number}"
    timeout = aiohttp.ClientTimeout(total=ctx.settings.api_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if not 200 <= resp.status < 300:
                text = await resp.text()
                raise RuntimeError(f"HTTP {resp.status}: {text}")
            data = await resp.json()
            if not isinstance(data, list):
                raise RuntimeError("Unexpected contacts payload")
            return data


def build_contacts_command(options: CommandOptions) -> CommandHandler:
    @command("!contacts")
    async def list_contacts(ctx: Context) -> None:
        text = (ctx.message.message or "").lower()
        base_url_override = options.faulty_contacts_base_url if "fault" in text else None
        label = "contacts(fault)" if base_url_override else "contacts"

        if base_url_override:
            await ctx.reply(
                SendMessageRequest(
                    message=f"forcing contacts against {base_url_override}",
                    recipients=[],
                )
            )

        result = await safe_api_call(
            ctx,
            label,
            _fetch_contacts(ctx, base_url_override),
        )
        if result is None:
            return
        await ctx.reply(
            SendMessageRequest(
                message=f"contacts found: {len(result)}",
                recipients=[],
            )
        )

    return list_contacts
