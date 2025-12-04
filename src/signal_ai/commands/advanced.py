from __future__ import annotations

import asyncio
import base64
import time
from typing import Iterable
from urllib.parse import parse_qs, urlparse

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.profiles import UpdateProfileRequest
from signal_client.infrastructure.schemas.receipts import ReceiptRequest
from signal_client.infrastructure.schemas.requests import (
    AddStickerPackRequest,
    MessageMention,
    RemoteDeleteRequest,
    SendMessageRequest,
)

from .types import CommandHandler
from .utils import safe_api_call


def _recipient(ctx: Context) -> str:
    if ctx.message.is_group() and ctx.message.group:
        return ctx.message.group["groupId"]
    return ctx.message.source


def _extract_pack_params(text: str) -> tuple[str | None, str | None]:
    tokens = text.split()
    pack_id = None
    pack_key = None
    for token in tokens:
        if token.startswith("!addpack"):
            continue
        parsed = urlparse(token)
        fragment = parse_qs(parsed.fragment)
        query = parse_qs(parsed.query)
        pack_id = fragment.get("pack_id", [None])[0] or query.get("pack_id", [None])[0] or pack_id
        pack_key = fragment.get("pack_key", [None])[0] or query.get("pack_key", [None])[0] or pack_key
        if pack_id and pack_key:
            break
        if not pack_id and not pack_key and len(token.split(":")) == 2:
            pack_id, pack_key = token.split(":", 1)
            break
    return pack_id, pack_key


def build_identities_command() -> CommandHandler:
    @command("!identities")
    async def identities(ctx: Context) -> None:
        result = await safe_api_call(
            ctx,
            "identities",
            ctx.identities.get_identities(ctx.settings.phone_number),
        )
        if result is None:
            return

        trusted = sum(1 for item in result if item.get("verified") or item.get("trusted"))
        await ctx.reply(
            SendMessageRequest(
                message=(
                    f"identities: {len(result)} entries "
                    f"({trusted} trusted) for {ctx.settings.phone_number}"
                ),
                recipients=[],
            )
        )

    return identities


def build_profile_command() -> CommandHandler:
    @command("!profile")
    async def profile(ctx: Context) -> None:
        raw = ctx.message.message or ""
        _, _, payload = raw.partition(" ")
        parts = [segment.strip() for segment in payload.split("|") if segment.strip()]
        if not parts:
            await ctx.reply(
                SendMessageRequest(
                    message=(
                        "usage: !profile <name>[|about][|base64_avatar]. "
                        "Example: !profile signal-ai bot|about text"
                    ),
                    recipients=[],
                )
            )
            return

        name = parts[0]
        about = parts[1] if len(parts) > 1 else None
        avatar = parts[2] if len(parts) > 2 else None
        request = UpdateProfileRequest(name=name, about=about, base64_avatar=avatar)
        await safe_api_call(
            ctx,
            "profile-update",
            ctx.profiles.update_profile(
                ctx.settings.phone_number, request.model_dump(exclude_none=True, by_alias=True)
            ),
        )
        parts_desc = [f"name='{name}'"]
        if about:
            parts_desc.append(f"about='{about}'")
        if avatar:
            parts_desc.append("avatar set")
        msg = "profile updated: " + ", ".join(parts_desc)
        await ctx.reply(
            SendMessageRequest(
                message=msg,
                recipients=[],
            )
        )

    return profile


def build_search_command() -> CommandHandler:
    @command("!search")
    async def search(ctx: Context) -> None:
        raw = ctx.message.message or ""
        parts: Iterable[str] = raw.split()
        numbers = [part for part in parts if not part.startswith("!search")]
        if not numbers:
            numbers = [ctx.message.source, ctx.settings.phone_number]

        result = await safe_api_call(
            ctx,
            "search",
            ctx.search.search_registered_numbers(ctx.settings.phone_number, numbers),
        )
        if result is None:
            return

        registered = [
            item.get("number")
            or item.get("input")
            or item.get("e164")
            or item.get("uuid")
            for item in result
            if item.get("isRegistered") is True or item.get("registered") is True
        ]
        await ctx.reply(
            SendMessageRequest(
                message=(
                    f"search: {len(registered)}/{len(result)} registered "
                    f"({', '.join(str(n) for n in registered if n) or 'none'})"
                ),
                recipients=[],
            )
        )

    return search


def build_sticker_packs_command() -> CommandHandler:
    @command("!packs")
    async def sticker_packs(ctx: Context) -> None:
        packs = await safe_api_call(
            ctx,
            "sticker-packs",
            ctx.sticker_packs.get_sticker_packs(ctx.settings.phone_number),
        )
        if packs is None:
            return
        if not packs:
            await ctx.reply(
                SendMessageRequest(
                    message="sticker packs: none installed",
                    recipients=[],
                )
            )
            return

        first = packs[0]
        pack_id = first.get("packId") or first.get("id") or first.get("pack_id") or "<unknown>"
        title = first.get("title") or first.get("name") or ""
        await ctx.reply(
            SendMessageRequest(
                message=(
                    f"sticker packs installed: {len(packs)}; "
                    f"first={pack_id}{f' ({title})' if title else ''}"
                ),
                recipients=[],
            )
        )

    return sticker_packs


def build_add_sticker_pack_command() -> CommandHandler:
    @command("!addpack")
    async def add_pack(ctx: Context) -> None:
        pack_id, pack_key = _extract_pack_params(ctx.message.message or "")
        if not pack_id or not pack_key:
            await ctx.reply(
                SendMessageRequest(
                    message=(
                        "usage: !addpack <signal.art url or pack_id:pack_key>. "
                        "Example: https://signal.art/addstickers/#pack_id=XXX&pack_key=YYY"
                    ),
                    recipients=[],
                )
            )
            return

        request = AddStickerPackRequest(pack_id=pack_id, pack_key=pack_key)
        await safe_api_call(
            ctx,
            "add-pack",
            ctx.sticker_packs.add_sticker_pack(
                ctx.settings.phone_number, request.model_dump()
            ),
        )
        await ctx.reply(
            SendMessageRequest(
                message=f"sticker pack added: {pack_id}",
                recipients=[],
            )
        )

    return add_pack


def build_view_once_command() -> CommandHandler:
    @command("!viewonce")
    async def view_once(ctx: Context) -> None:
        payload = SendMessageRequest(
            message="view-once attachment demo",
            recipients=[],
            base64_attachments=[
                base64.b64encode(b"signal-ai view-once validation").decode()
            ],
            view_once=True,
        )
        await safe_api_call(ctx, "view-once", ctx.send(payload))

    return view_once


def build_quote_mentions_command() -> CommandHandler:
    @command("!quotemention")
    async def quote_mentions(ctx: Context) -> None:
        quote_text = ctx.message.message or ""
        mention_length = min(len(ctx.message.source), len(quote_text))
        mentions = (
            [MessageMention(author=ctx.message.source, start=0, length=mention_length)]
            if mention_length
            else None
        )
        await ctx.reply(
            SendMessageRequest(
                message="replying with quote mentions",
                recipients=[],
                quote_mentions=mentions,
            )
        )

    return quote_mentions


def build_sticker_command() -> CommandHandler:
    @command("!sticker")
    async def sticker(ctx: Context) -> None:
        packs = await safe_api_call(
            ctx,
            "sticker-packs",
            ctx.sticker_packs.get_sticker_packs(ctx.settings.phone_number),
        )
        if packs is None:
            return
        if not packs:
            await ctx.reply(
                SendMessageRequest(
                    message="install a sticker pack first",
                    recipients=[],
                )
            )
            return

        pack = packs[0]
        pack_id = pack.get("packId") or pack.get("id") or pack.get("pack_id")
        if not pack_id:
            await ctx.reply(
                SendMessageRequest(
                    message="sticker pack missing packId",
                    recipients=[],
                )
            )
            return

        sticker_id = 0
        sticker_ref = f"{pack_id}:{sticker_id}"

        await safe_api_call(
            ctx,
            "sticker",
            ctx.send(
                SendMessageRequest(
                    message=f"sticker {sticker_ref}",
                    recipients=[],
                    sticker=sticker_ref,
                )
            ),
        )

    return sticker


def build_receipt_command() -> CommandHandler:
    @command("!receipt")
    async def receipt(ctx: Context) -> None:
        recipient = _recipient(ctx)
        receipt_request = ReceiptRequest(
            recipient=None if ctx.message.is_group() else recipient,
            group=recipient if ctx.message.is_group() else None,
            timestamp=ctx.message.timestamp,
        )
        await safe_api_call(
            ctx,
            "receipt",
            ctx.receipts.send_receipt(
                ctx.settings.phone_number,
                receipt_request.model_dump(exclude_none=True, by_alias=True),
            ),
        )
        await ctx.reply(
            SendMessageRequest(
                message=f"receipt sent for {receipt_request.timestamp}",
                recipients=[],
            )
        )

    return receipt


def build_typing_command() -> CommandHandler:
    @command("!typing")
    async def typing(ctx: Context) -> None:
        if ctx.message.source == ctx.settings.phone_number:
            await ctx.reply(
                SendMessageRequest(
                    message="typing indicator only shows to other recipients; use a second number/group to observe it",
                    recipients=[],
                )
            )
            return
        await ctx.start_typing()
        try:
            await asyncio.sleep(2)
        finally:
            await ctx.stop_typing()
        await ctx.reply(
            SendMessageRequest(
                message="typing indicator toggled",
                recipients=[],
            )
        )

    return typing


def build_remote_delete_command() -> CommandHandler:
    @command("!delete")
    async def remote_delete(ctx: Context) -> None:
        recipient = _recipient(ctx)
        send_request = SendMessageRequest(
            message="temporary message to delete",
            recipients=[recipient],
            number=ctx.settings.phone_number,
        )
        send_payload = send_request.model_dump(exclude_none=True)
        result = await safe_api_call(
            ctx,
            "send-for-delete",
            ctx.messages.send(send_payload),
        )
        if result is None:
            return

        timestamp_raw = result.get("timestamp") if isinstance(result, dict) else None
        try:
            timestamp = int(timestamp_raw) if timestamp_raw is not None else None
        except (TypeError, ValueError):
            timestamp = None

        if timestamp is None:
            await ctx.reply(
                SendMessageRequest(
                    message="remote delete: could not read timestamp from send response",
                    recipients=[],
                )
            )
            return

        await asyncio.sleep(1)
        delete_request = RemoteDeleteRequest(recipient=recipient, timestamp=timestamp)
        await safe_api_call(
            ctx,
            "remote-delete",
            ctx.messages.remote_delete(
                ctx.settings.phone_number, delete_request.model_dump(exclude_none=True)
            ),
        )
        await ctx.reply(
            SendMessageRequest(
                message=f"remote delete issued for {timestamp}",
                recipients=[],
            )
        )

    return remote_delete


def build_resilience_command() -> CommandHandler:
    @command("!resilience")
    async def resilience(ctx: Context) -> None:
        attempts = 3
        durations: list[float] = []
        for _ in range(attempts):
            start = time.monotonic()w
            result = await safe_api_call(ctx, "health", ctx.general.get_health())
            if result is None:
                return
            durations.append(time.monotonic() - start)

        avg_ms = int((sum(durations) / len(durations)) * 1000) if durations else 0
        await ctx.reply(
            SendMessageRequest(
                message=(
                    "resilience: "
                    f"rate_limit={ctx.settings.rate_limit}/{ctx.settings.rate_limit_period}s, "
                    f"cb_threshold={ctx.settings.circuit_breaker_failure_threshold}, "
                    f"cb_reset={ctx.settings.circuit_breaker_reset_timeout}s, "
                    f"avg_health={avg_ms}ms"
                ),
                recipients=[],
            )
        )

    return resilience
