from __future__ import annotations

import structlog

from signal_client import SignalClient
from signal_client.config import Settings
from signal_client.metrics_server import start_metrics_server
from signal_client.health_server import start_health_server, HealthServer

from .commands import CommandOptions, build_command_handlers
from .config import AppConfig
from .middlewares import blocklist_middleware, dlq_middleware, timing_middleware
from .services.dlq import replay_dlq_once
from .services.health import (
    ensure_signal_api_running,
    health_check,
    report_status,
    warm_api_session,
)

log = structlog.get_logger()


def _startup_log(settings: Settings, dlq_enabled: bool) -> None:
    backpressure = "drop_oldest" if settings.queue_drop_oldest_on_timeout else "fail_fast"
    log.info(
        "signal_ai.startup",
        phone_number=settings.phone_number,
        signal_service=settings.signal_service,
        base_url=settings.base_url,
        storage=settings.storage_type,
        sqlite_db=settings.sqlite_database,
        redis_host=settings.redis_host,
        redis_port=settings.redis_port,
        queue_size=settings.queue_size,
        queue_timeout=settings.queue_put_timeout,
        queue_policy=backpressure,
        workers=settings.worker_pool_size,
        retries=settings.api_retries,
        backoff=settings.api_backoff_factor,
        api_timeout=settings.api_timeout,
        dlq_enabled=dlq_enabled,
        dlq_name=settings.dlq_name,
        dlq_max_retries=settings.dlq_max_retries,
    )


async def _run_bot(config: AppConfig) -> None:
    overrides: dict[str, object] = {}
    ensure_signal_api_running(config.auto_start_signal_api)
    settings = Settings.from_sources(config=overrides)
    await health_check(settings, timeout=config.health_timeout)
    single_number_mode = not config.secondary_member or config.secondary_member == settings.phone_number

    if config.start_metrics_server:
        start_metrics_server(port=config.metrics_port, addr=config.metrics_host)

    health_server: HealthServer | None = None
    async with SignalClient(config=overrides) as bot:
        _startup_log(bot.settings, bot.app.dead_letter_queue is not None)
        if single_number_mode:
            log.info("signal_ai.single_number_mode", phone_number=bot.settings.phone_number)

        if config.warm_api_session:
            await warm_api_session(bot)

        command_options = CommandOptions(
            admin_number=config.admin_number or bot.settings.phone_number,
            faulty_contacts_base_url=config.faulty_contacts_base_url,
            secondary_member=config.secondary_member,
        )
        for handler in build_command_handlers(command_options):
            # Ensure the admin whitelist defaults to the bot number if not provided.
            if getattr(handler, "name", None) == "!admin" and not handler.whitelisted:
                handler.whitelisted = [bot.settings.phone_number]  # type: ignore[attr-defined]
            bot.register(handler)

        bot.use(dlq_middleware(bot.app.dead_letter_queue))
        bot.use(blocklist_middleware(config.blocklist))
        bot.use(timing_middleware)

        if config.start_health_server:
            health_server = await start_health_server(
                bot.app,
                host=config.health_host,
                port=config.health_port,
            )

        try:
            await bot.start()
        finally:
            if health_server is not None:
                await health_server.stop()


async def run(config: AppConfig) -> None:
    if config.status_only:
        await report_status(config)
        return
    if config.replay_dlq:
        await replay_dlq_once()
        return
    await _run_bot(config)
