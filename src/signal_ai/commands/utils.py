from __future__ import annotations

from typing import Any, Awaitable

import asyncio
import structlog

from signal_client import Context
from signal_client.infrastructure.schemas.requests import SendMessageRequest

log = structlog.get_logger()


async def safe_api_call(ctx: Context, label: str, coro: Awaitable[Any]) -> Any | None:
    try:
        return await coro
    except Exception as exc:  # noqa: BLE001
        error_text = "request timed out" if isinstance(exc, asyncio.TimeoutError) else str(exc)
        if not error_text:
            error_text = exc.__class__.__name__
        log.warning("command.api_failed", command=label, error=error_text, exc_info=exc)
        await ctx.reply(
            SendMessageRequest(
                message=f"{label} failed: {error_text}",
                recipients=[],
            )
        )
        return None
