# signal-ai

Signal bot skeleton built on top of the local [`signal-client`](../signal-client) framework.

## Prerequisites
- Python 3.9–3.13.
- Local signal-client checkout at `../signal-client` (path dependency).
- Docker up with `bbernhard/signal-cli-rest-api` reachable (HTTP + websocket).

## Setup
```bash
# 1) Install signal-client dependencies once
cd ../signal-client && poetry install --sync

# 2) Install signal-ai (uses the local signal-client path dependency)
cd ../signal-ai && poetry install --sync

# 3) Run signal-cli-rest-api in json-rpc mode (reuses your linked config volume)
docker rm -f signal-api 2>/dev/null || true
docker run -d --name signal-api --restart=always -p 8080:8080 \
  -v $HOME/.local/share/signal-api:/home/.local/share/signal-cli \
  -e MODE=json-rpc bbernhard/signal-cli-rest-api:0.95
```

Required environment:
- `SIGNAL_PHONE_NUMBER` (E.164, e.g. `+15551234567`)
- `SIGNAL_SERVICE_URL` (HTTP base, used to derive ws/wss, e.g. `http://localhost:8080`)
- `SIGNAL_API_URL` (HTTP base, usually same as service URL)

Common knobs (all optional):
- Storage: `STORAGE_TYPE` (`sqlite`|`redis`), `SQLITE_DATABASE`, `REDIS_HOST`, `REDIS_PORT`
- Queue/backpressure: `QUEUE_SIZE`, `QUEUE_PUT_TIMEOUT`, `QUEUE_DROP_OLDEST_ON_TIMEOUT`, `WORKER_POOL_SIZE`
- DLQ: `DLQ_NAME`, `DLQ_MAX_RETRIES`
- API resiliency: `API_RETRIES`, `API_BACKOFF_FACTOR`, `API_TIMEOUT`, `RATE_LIMIT`, `RATE_LIMIT_PERIOD`, `CIRCUIT_BREAKER_*`
- Metrics: `METRICS_HOST` (default `0.0.0.0`), `METRICS_PORT` (default `9000`)

## Run
```bash
poetry run python main.py
```

Example command available: `!ping` replies with `pong`. Metrics exposed at `/` on `METRICS_HOST:METRICS_PORT`.

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
