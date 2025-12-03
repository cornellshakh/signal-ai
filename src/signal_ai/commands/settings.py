from __future__ import annotations

from signal_client import Context
from signal_client.command import command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

from .types import CommandHandler


def build_settings_command() -> CommandHandler:
    @command("!settings")
    async def settings_echo(ctx: Context) -> None:
        settings = ctx.settings
        backpressure = "drop_oldest" if settings.queue_drop_oldest_on_timeout else "fail_fast"
        await ctx.reply(
            SendMessageRequest(
                message=(
                    "settings: "
                    f"workers={settings.worker_pool_size}, "
                    f"queue={settings.queue_size} ({backpressure}), "
                    f"retries={settings.api_retries}, "
                    f"backoff={settings.api_backoff_factor}, "
                    f"timeout={settings.api_timeout}, "
                    f"storage={settings.storage_type}, "
                    f"dlq={settings.dlq_name}/{settings.dlq_max_retries}"
                ),
                recipients=[],
            )
        )

    return settings_echo
