from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import structlog

from signal_client import SignalClient
from signal_client.observability.metrics import DLQ_BACKLOG
from signal_client.runtime.models import QueuedMessage

log = structlog.get_logger()


async def replay_dlq_once() -> None:
    overrides: dict[str, object] = {}
    async with SignalClient(config=overrides) as bot:
        if bot.app.dead_letter_queue is None:
            raise RuntimeError("DLQ not configured; set STORAGE/DLQ env.")
        if bot.app.queue is None or bot.app.worker_pool is None:
            raise RuntimeError("Runtime not initialized; queue/worker_pool missing.")

        ready: List[Dict[str, Any]] = await bot.app.dead_letter_queue.replay()
        if not ready:
            log.info("dlq.empty")
            return

        queue = bot.app.queue
        worker_pool = bot.app.worker_pool

        for record in ready:
            payload = record.get("payload") if isinstance(record, dict) else record
            raw = payload if isinstance(payload, str) else json.dumps(payload)
            await queue.put(QueuedMessage(raw=raw, enqueued_at=time.perf_counter()))  # type: ignore[arg-type]

        worker_pool.start()
        await queue.join()
        worker_pool.stop()
        await worker_pool.join()

        DLQ_BACKLOG.labels(queue=bot.settings.dlq_name).set(0)
        log.info("dlq.replayed", count=len(ready))
