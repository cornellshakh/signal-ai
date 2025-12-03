from __future__ import annotations

import time
from typing import Awaitable, Callable, Coroutine

import structlog

from signal_client import Context
from signal_client.services.dead_letter_queue import DeadLetterQueue

log = structlog.get_logger()

MiddlewareCallable = Callable[
    [Context, Callable[[Context], Awaitable[None]]], Awaitable[None]
]


def dlq_middleware(dlq: DeadLetterQueue | None) -> MiddlewareCallable:
    async def middleware(
        ctx: Context, next_callable: Callable[[Context], Awaitable[None]]
    ) -> None:
        try:
            await next_callable(ctx)
        except Exception as exc:  # noqa: BLE001
            log.error("command.exception", error=str(exc))
            if dlq is not None:
                payload = {
                    "envelope": {
                        "source": ctx.message.source,
                        "timestamp": ctx.message.timestamp,
                        "dataMessage": {
                            "message": ctx.message.message,
                            "timestamp": ctx.message.timestamp,
                        },
                    }
                }
                if ctx.message.group:
                    payload["envelope"]["dataMessage"]["groupInfo"] = ctx.message.group
                await dlq.send(payload)
            raise

    return middleware


async def timing_middleware(
    ctx: Context, next_callable: Callable[[Context], Awaitable[None]]
) -> None:
    started = time.perf_counter()
    await next_callable(ctx)
    elapsed_ms = (time.perf_counter() - started) * 1000
    log.info(
        "command.timing",
        command=ctx.message.message,
        elapsed_ms=elapsed_ms,
        worker=structlog.contextvars.get_contextvars().get("worker_id"),
    )


def blocklist_middleware(blocklist: set[str]) -> MiddlewareCallable:
    async def middleware(
        ctx: Context, next_callable: Callable[[Context], Awaitable[None]]
    ) -> None:
        if ctx.message.source in blocklist:
            log.info("command.blocked", source=ctx.message.source)
            return
        await next_callable(ctx)

    return middleware
