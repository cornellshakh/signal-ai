from __future__ import annotations

import random
import re

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler

ROLL_PATTERN = re.compile(r"!roll\s+(\d+)d(\d+)", re.IGNORECASE)


def build_roll_command() -> CommandHandler:
    @command(ROLL_PATTERN)
    async def roll(ctx: Context) -> None:
        match = ROLL_PATTERN.search(ctx.message.message or "")
        if not match:
            return
        count, sides = int(match.group(1)), int(match.group(2))
        rolls = [random.randint(1, sides) for _ in range(count)]
        await ctx.reply(
            SendMessageRequest(
                message=f"rolled {count}d{sides}: {rolls} (total={sum(rolls)})",
                recipients=[],
            )
        )

    return roll
