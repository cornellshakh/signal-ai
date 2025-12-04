from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import aiohttp
import structlog

from signal_client import SignalClient
from signal_client.config import Settings

from ..config import AppConfig

log = structlog.get_logger()


def ensure_signal_api_running(auto_start: bool) -> None:
    if not auto_start:
        return

    scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
    manage_path = scripts_dir / "manage_signal_api.py"
    if not manage_path.exists():
        log.warning("signal_api.starter_missing", path=str(manage_path))
        return

    cmd = [sys.executable, str(manage_path), "start"]
    result = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        log.warning(
            "signal_api.start_failed",
            code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    else:
        log.info("signal_api.ensure_running", stdout=result.stdout.strip())


def _build_ws_url(settings: Settings) -> str:
    service_url = settings.signal_service.rstrip("/")
    if service_url.startswith("https://"):
        ws_base = f"wss://{service_url[len('https://'):]}"
    elif service_url.startswith("http://"):
        ws_base = f"ws://{service_url[len('http://'):]}"
    else:
        ws_base = f"ws://{service_url}"
    ws_path = settings.websocket_path or f"/v1/receive/{settings.phone_number}"
    return f"{ws_base}{ws_path}"


async def health_check(settings: Settings, timeout: float) -> None:
    service_url = settings.signal_service.rstrip("/")
    http_url = f"{service_url}/v1/health"
    ws_url = _build_ws_url(settings)
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        async with session.get(http_url) as resp:
            body = await resp.text()
            if not 200 <= resp.status < 300:
                message = f"HTTP health failed ({resp.status}): {body}"
                raise RuntimeError(message)

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        async with session.ws_connect(ws_url, heartbeat=10) as ws:
            await ws.close()


async def warm_api_session(bot: SignalClient) -> None:
    started = time.perf_counter()
    try:
        await bot.api_clients.general.get_health()
    except Exception as exc:  # noqa: BLE001
        log.warning("signal_ai.warmup_failed", error=str(exc))
        return
    elapsed_ms = (time.perf_counter() - started) * 1000
    log.info("signal_ai.warmup", elapsed_ms=elapsed_ms)


async def report_status(config: AppConfig) -> None:
    settings = Settings.from_sources(config={})
    http_health_ok = True
    try:
        await health_check(settings, timeout=config.health_timeout)
    except Exception as exc:  # noqa: BLE001
        http_health_ok = False
        log.error("signal_ai.health_check_failed", error=str(exc))

    dlq_enabled = False
    dlq_depth = 0
    ingest_paused_until: float | None = None
    persistent_queue_enabled = False

    async with SignalClient(config={}) as bot:
        dlq = bot.app.dead_letter_queue
        if dlq is not None:
            dlq_enabled = True
            entries = await dlq.inspect()
            dlq_depth = len(entries)
        if bot.app.intake_controller is not None:
            snapshot = bot.app.intake_controller.snapshot()
            ingest_paused_until = snapshot.get("paused_until")  # type: ignore[arg-type]
        persistent_queue_enabled = bot.app.persistent_queue is not None

    ready = http_health_ok
    log.info(
        "signal_ai.status",
        ready=ready,
        http_health_ok=http_health_ok,
        dlq_enabled=dlq_enabled,
        dlq_depth=dlq_depth,
        ingest_paused_until=ingest_paused_until,
        persistent_queue_enabled=persistent_queue_enabled,
    )
    if not ready:
        message = "Health check failed"
        raise RuntimeError(message)
