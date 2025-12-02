import asyncio
import os

from signal_client import Context, SignalClient
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest
from signal_client.observability.logging import ensure_structlog_configured
from signal_client.observability.metrics import start_metrics_server


@command("!ping")
async def ping(ctx: Context) -> None:
    await ctx.reply(SendMessageRequest(message="pong", recipients=[]))


async def run_bot() -> None:
    ensure_structlog_configured()

    async with SignalClient() as bot:
        bot.register(ping)
        await bot.start()


def _maybe_start_metrics_server() -> None:
    host = os.getenv("METRICS_HOST", "0.0.0.0")
    port = int(os.getenv("METRICS_PORT", "9000"))
    start_metrics_server(port=port, addr=host)


if __name__ == "__main__":
    _maybe_start_metrics_server()
    asyncio.run(run_bot())
