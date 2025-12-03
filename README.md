# signal-ai

Signal bot skeleton built on top of the local [`signal-client`](../signal-client) framework.

## Prerequisites
- Python 3.9–3.13.
- Local signal-client checkout at `../signal-client` (path dependency).
- Docker running `bbernhard/signal-cli-rest-api` (HTTP + websocket).

## Setup
```bash
# 1) Install signal-client dependencies once
cd ../signal-client && poetry install --sync

# 2) Install signal-ai (uses the local signal-client path dependency)
cd ../signal-ai && poetry install --sync

# 3) Run signal-cli-rest-api (json-rpc mode)
docker rm -f signal-api 2>/dev/null || true
docker run -d --name signal-api --restart=always -p 8080:8080 \
  -v $HOME/.local/share/signal-api:/home/.local/share/signal-cli \
  -e MODE=json-rpc bbernhard/signal-cli-rest-api:0.95
```

Required environment:
- `SIGNAL_PHONE_NUMBER` (E.164, e.g. `+15551234567`)
- `SIGNAL_SERVICE_URL` (HTTP base, used to derive ws/wss, e.g. `http://localhost:8080`)
- `SIGNAL_API_URL` (HTTP base, usually same as service URL)

Optional knobs:
- Storage: `STORAGE_TYPE` (`sqlite`|`redis`), `SQLITE_DATABASE`, `REDIS_HOST`, `REDIS_PORT`
- Queue/backpressure: `QUEUE_SIZE`, `QUEUE_PUT_TIMEOUT`, `QUEUE_DROP_OLDEST_ON_TIMEOUT`, `WORKER_POOL_SIZE`
- DLQ: `DLQ_NAME`, `DLQ_MAX_RETRIES`
- API resiliency: `API_RETRIES`, `API_BACKOFF_FACTOR`, `API_TIMEOUT`, `RATE_LIMIT`, `RATE_LIMIT_PERIOD`, `CIRCUIT_BREAKER_*`
- Metrics: `METRICS_HOST` (default `0.0.0.0`), `METRICS_PORT` (default `9000`)
- Validation helpers: `SECONDARY_MEMBER` (group creation), `ADMIN_NUMBER`, `BLOCKLISTED`, `FAULT_BASE_URL`

## Layout (src/ package)
- `src/signal_ai/app.py`: bootstrap and runtime wiring.
- `src/signal_ai/config.py`: CLI/env parsing.
- `src/signal_ai/commands/`: command handlers and shared state.
- `src/signal_ai/middlewares.py`: middleware helpers.
- `src/signal_ai/services/`: health checks, DLQ replay.
- `main.py`: thin wrapper calling `signal_ai.cli`.

## Run
```bash
poetry run python main.py
```

Flags (see `poetry run python main.py --help`):
- Default mode targets your own number (notes-to-self). Group creation is skipped unless `SECONDARY_MEMBER` is set to a different number.
- `--replay-dlq`: replay ready DLQ entries once, then exit.
- `--no-api-autostart`: skip Docker auto-start of signal-cli-rest-api.
- `--no-warmup`: skip initial HTTP warmup call.
- `--no-metrics`: do not start the embedded Prometheus server.
- `--health-timeout`, `--blocklist`, `--faulty-contacts-base-url`, `--secondary-member`, `--admin-number`.

Metrics exposed at `/` on `METRICS_HOST:METRICS_PORT` (defaults 0.0.0.0:9000).

## Commands (validation sweep)
- `!ping`, `!settings`, `!echo ...`
- `!react` (adds and removes the bot reaction)
- `!share` (attachment + mention + preview)
- `!balance` (lock-protected counter), `!roll 2d6`
- `!admin` (whitelist; defaults to the bot number or `ADMIN_NUMBER`)
- `!contacts` (`!contacts fault` uses `FAULT_BASE_URL` to exercise retries)
- `!history`, `!newgroup` (skips unless `SECONDARY_MEMBER` is set)
- `!dlq-fail` (forces an exception so DLQ replay can be tested)

## Utilities
- Replay DLQ: `poetry run python main.py --replay-dlq`

## Validation
- `poetry run ruff check .`
- `poetry run black --check .`
- `poetry run mypy .`
- Add bot-specific tests as handlers grow.

## Smoke REST (optional)
```bash
curl -X POST "$SIGNAL_API_URL/v2/send" \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"hi\",\"number\":\"$SIGNAL_PHONE_NUMBER\",\"recipients\":[\"$SIGNAL_PHONE_NUMBER\"]}"
```
