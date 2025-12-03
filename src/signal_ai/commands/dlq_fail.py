from __future__ import annotations

from signal_client import Context
from signal_client.command import command

from .types import CommandHandler


def build_dlq_fail_command() -> CommandHandler:
    @command("!dlq-fail")
    async def dlq_fail(ctx: Context) -> None:
        raise RuntimeError("intentional failure for DLQ replay")

    return dlq_fail
