# Signal Client notes for signal-ai

Keep this around when writing the bot so you don’t have to re-remember how the client works.

- Codebase: `/home/user/Work/signal/signal-client` (install once: `poetry install --sync`).
- Backend it needs: `bbernhard/signal-cli-rest-api` (provides REST + websocket). Required env: `SIGNAL_PHONE_NUMBER`, `SIGNAL_SERVICE_URL`, `SIGNAL_API_URL`.
- Common knobs: storage (`STORAGE_TYPE`, `SQLITE_DATABASE`, `REDIS_HOST`, `REDIS_PORT`), queue/backpressure (`QUEUE_SIZE`, `QUEUE_PUT_TIMEOUT`, `QUEUE_DROP_OLDEST_ON_TIMEOUT`, `WORKER_POOL_SIZE`), DLQ (`DLQ_NAME`, `DLQ_MAX_RETRIES`), API resiliency (`API_RETRIES`, `API_BACKOFF_FACTOR`, `API_TIMEOUT`, `RATE_LIMIT`, `RATE_LIMIT_PERIOD`, `CIRCUIT_BREAKER_*`).

## How the runtime works
- `SignalClient.start()` wires everything: websocket listener → enqueue with backpressure → worker pool → command router → handler.
- Websocket (`WebSocketClient`): builds ws/wss URL from `SIGNAL_SERVICE_URL` and phone number, auto-reconnects, yields raw JSON strings.
- Queue/backpressure (`MessageService`): puts messages on an `asyncio.Queue`; drop-oldest is default, fail-fast is optional. Dropped messages can go to DLQ.
- Workers (`WorkerPool`): parse JSON via `MessageParser` into `Message` model, then route to commands. Bad payloads are discarded quietly with metrics.
- Command router: preserves registration order; literals checked before regex; whitelisting restricts by sender. Middleware wraps handlers in order of registration.

## Commands and Context
- Define with `@command("!foo")` and `bot.register(cmd)` before start. Router only runs when `Context.message.message` is a non-empty string.
- `Context` helpers:
  - `send(SendMessageRequest)`: fills recipients with sender/group if empty; defaults `number` to our phone.
  - `reply(...)`: quotes the incoming message automatically.
  - `react(emoji)` / `remove_reaction()`.
  - `start_typing()` / `stop_typing()`.
  - `lock(resource_id)`: async lock per key (in-memory).
- Message model: `message`, `source`, `timestamp`, `group` (with `groupId`), `reaction_*`, `attachments_local_filenames`, `mentions`, `type` in `{DATA_MESSAGE, SYNC_MESSAGE, EDIT_MESSAGE, DELETE_MESSAGE}`. `recipient()` chooses group id or sender.

## REST clients (what you can call)
- Messages: send, get history, remote delete, typing indicators.
- Reactions: send/remove.
- Receipts: send.
- Groups: list/create/update/delete; add/remove admins/members; block/unblock; join/quit; set/get avatar.
- Contacts: list/get/update; sync; get avatar; block/unblock.
- Identities: list; trust.
- Devices: list/add/remove; QR link; register/verify/unregister.
- Accounts: list/get; set/remove device name, PIN, registration lock, username; lift rate limit; update settings.
- Profiles: get/update; get avatar.
- Sticker packs: list/add; fetch a sticker.
- Attachments: list; fetch; remove.
- Search: check which numbers are registered.
- General: about/health; get/set configuration; get/set per-account mode/settings.
- All clients share retries/backoff/timeouts, optional rate limiter, and circuit breaker; errors map to typed exceptions.

## Message edge cases
- Edits → `type=EDIT_MESSAGE`, `target_sent_timestamp` set.
- Deletes → `type=DELETE_MESSAGE`, `remote_delete_timestamp` set.
- Reactions populate `reaction_emoji`, `reaction_target_author`, `reaction_target_timestamp`.
- Mentions captured in `mentions`; attachment filenames in `attachments_local_filenames`.
- Sync messages → `type=SYNC_MESSAGE` (from `syncMessage.sentMessage`).

## Storage and DLQ
- Storage abstraction: SQLite by default (`signal_client.db`), Redis optional.
- DLQ: `DeadLetterQueue` stores payloads with exponential backoff and max retries. Inspect via `python -m signal_client.cli dlq inspect` or `poetry run inspect-dlq`.

## Observability and ops
- Metrics: processed messages, queue depth/latency, errors, DLQ depth, rate limiter wait, circuit breaker state, API latency. Expose with `from signal_client.observability.metrics import start_metrics_server; start_metrics_server(port=9000, addr="0.0.0.0")`.
- Logging: `ensure_structlog_configured()` sets sane defaults unless you configured structlog already.
- Compatibility guard: on import, checks pydantic/structlog/aiohttp versions against vetted ranges.
- Quality gates (in signal-client): `poetry run ruff check .`, `poetry run black --check src tests`, `poetry run mypy src`, `poetry run pytest-safe -n auto --cov=signal_client`.

## Quick start (signal-ai)
1) Install signal-client deps once: `cd /home/user/Work/signal/signal-client && poetry install --sync`.
2) Make sure your `signal-cli-rest-api` container is up (mode native, persistent volume). Start/verify Docker before launching the bot.
3) In signal-ai, create `main.py`:
```python
import asyncio
from signal_client import SignalClient, Context, command
from signal_client.infrastructure.schemas.requests import SendMessageRequest

@command("!ping")
async def ping(ctx: Context) -> None:
    await ctx.reply(SendMessageRequest(message="pong", recipients=[]))

async def main() -> None:
    async with SignalClient() as bot:
        bot.register(ping)
        await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```
4) Export env:
   - `SIGNAL_PHONE_NUMBER` (E.164, e.g. +15551234567)
   - `SIGNAL_SERVICE_URL` (HTTP base; becomes ws/wss internally, e.g. http://localhost:8080)
   - `SIGNAL_API_URL` (same HTTP base)
   - Optional: `STORAGE_TYPE` (sqlite|redis), `SQLITE_DATABASE` or `REDIS_HOST`/`REDIS_PORT`, `WORKER_POOL_SIZE`, `QUEUE_SIZE`, `QUEUE_DROP_OLDEST_ON_TIMEOUT`, `DLQ_MAX_RETRIES`, `API_RETRIES`, `API_TIMEOUT`, `RATE_LIMIT`, `RATE_LIMIT_PERIOD`.
5) Run: `poetry run python main.py`.

## Local testing
- Smoke REST: `curl -X POST http://localhost:8080/v2/send -H 'Content-Type: application/json' -d '{"message":"hi","number":"$SIGNAL_PHONE_NUMBER","recipients":["$SIGNAL_PHONE_NUMBER"]}'`
- After signal-client changes: `poetry run ruff check . && poetry run black --check src tests && poetry run mypy src && poetry run pytest-safe -n auto --cov=signal_client`.
- For bot code, add handler/middleware tests; `tests/integration/test_end_to_end.py` in signal-client shows a stub websocket pattern.

## Storage quick call
- SQLite: simplest, single process, file in CWD (`signal_client.db`).
- Redis: set `STORAGE_TYPE=redis` + host/port; use for multi-process or durable DLQ.

## Common gotchas
- 401/403: wrong `SIGNAL_API_URL` or number not registered/linked.
- No websocket messages: wrong `SIGNAL_SERVICE_URL`, wrong number, or scheme not http/https/ws/wss.
- Queue overflow: bump `QUEUE_SIZE`, raise `WORKER_POOL_SIZE`, or set `QUEUE_DROP_OLDEST_ON_TIMEOUT=false` and rely on DLQ.
- Empty `Context.message.message`: router skips attachments-only/empty messages unless you handle them manually.
- Circuit breaker/rate limit trips: tune `CIRCUIT_BREAKER_*` and `RATE_LIMIT`/`RATE_LIMIT_PERIOD`; check upstream health.
