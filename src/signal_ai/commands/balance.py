from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import BotState, CommandHandler


def build_balance_command(state: BotState) -> CommandHandler:
    @command("!balance")
    async def balance(ctx: Context) -> None:
        user = ctx.message.source
        key = f"balance:{user}"
        async with ctx.lock(key):
            current = state.balances.get(user, 100)
            state.balances[user] = current + 10
            await ctx.reply(
                SendMessageRequest(
                    message=f"balance for {user}: {state.balances[user]}",
                    recipients=[],
                )
            )

    return balance
