# Perfect Bot SDK Refactor Checklist

Purpose: turn `signal-client` from a thin signal-cli-rest-api wrapper into a robust, batteries-included bot SDK. Each task is spelled out so you can execute without recalling prior context.

## Ground rules
- [ ] Keep websocket as primary ingest; REST history stays unsupported.
- [ ] Preserve required envs: `SIGNAL_PHONE_NUMBER`, `SIGNAL_SERVICE_URL`, `SIGNAL_API_URL`.
- [ ] Default storage stays SQLite; Redis remains optional via DI.
- [ ] Do not break public helpers (`send_*`, `reply_*`, reactions, typing, receipts, remote delete) without a clear migration note.

## Ingest durability and backpressure
- [x] Add durable checkpointing for websocket ingest: record last processed `timestamp`/`enqueued_at` and resume after restarts; include duplicate suppression by `(source, timestamp)`.
- [x] Optionally back ingest by a persistent queue (SQLite/Redis stream/Kafka) so messages survive crashes; guard with feature flag/config.
- [x] When backpressure persists or circuit breaker is open, pause websocket intake and log/metric the pause/resume events. *(Backpressure pause/metric added; circuit breaker linkage now wired to circuit breaker state changes.)*
- [x] Ensure dropped or failed messages (enqueue timeout, parse error, handler error) are sent to DLQ with enough context to replay.

## Ordering and concurrency
- [x] Introduce per-conversation ordering: shard the worker pool by `recipient` (groupId or source) so messages for the same conversation stay ordered. *(CRC32(recipient) → shard; lock manager enforces serialization per recipient even with multiple workers.)*
- [x] Provide a distributed lock option (Redis key) for multi-process deployments; keep the current in-process lock as default.
- [x] Make worker pool size and shard count configurable; document the mapping function and its limits. *(New `worker_shard_count` config defaults to `worker_pool_size`; shard count must be ≤ pool size.)*

## Message and event modeling
- [x] Expand envelope parsing to typed models for receipts, typing indicators, calls, verified status changes, blocks, and other Signal events; expose them as first-class events instead of raw JSON. *(New event schemas + `parse_event` return `MessageEvent`/`ReceiptEvent`/`TypingEvent`/`CallEvent`/`VerificationEvent`/`BlockEvent`; message parsing remains backward compatible.)*
- [x] Support attachments end-to-end: helper to download attachments to temp files/streams with size/type limits and cleanup. *(Attachment pointers are parsed; `Context.download_attachments` wraps new downloader with a 25MB default cap and temp-dir cleanup.)*
- [x] Keep backward-compatible fields (e.g., `groupInfo` alias) but prefer normalized names. *(Message schema now accepts `groupInfo` alias while exposing normalized `group`.)*

## API clients and resiliency
- [x] Add auth/header hooks for secured signal-cli-rest-api deployments. *(ClientConfig now accepts default headers + async header providers; Settings can inject Authorization and extra headers.)*
- [x] Add per-endpoint timeouts and idempotency tokens where applicable; expose retries/backoff per client. *(Per-path timeout overrides, RequestOptions for per-call retries/backoff/headers/idempotency, Send/remote-delete support idempotency keys.)*
- [ ] Return typed response models instead of untyped dicts; surface normalized errors with docs links.
- [x] Wire rate limiter and circuit breaker state to ingest: when APIs are throttled or open, slow/stop intake and surface metrics. *(Circuit breaker pauses intake on open; rate limiter now pauses ingest for observed wait durations and records pause metrics.)*

## Context and helper ergonomics
- [ ] Add high-level helpers for media (download + send), mentions/quotes for edited messages, stickers, view-once, link previews with safe defaults.
- [ ] Include conversation/session helper (per-contact/group) for storing ephemeral state and rate limiting per user/group.
- [ ] Ensure every helper backfills recipients/number automatically and is idempotent when retries happen. *(Send/reply already backfill recipient/number; idempotency keys supported on send/remote-delete. Remaining: propagate through other helpers + retry flows.)*
- [x] Expose a simple middleware API for before/after hooks (logging, auth, quota). *(SignalClient.use registers middleware; worker pool runs middleware chain around handlers.)*

## Observability and ops
- [x] Add metrics for websocket lifecycle (connect, reconnects, failures), command latency/success/failure, DLQ enqueue/replay results, queue depth per shard, and backpressure pauses. *(Websocket connection state/events, command latency/outcomes, DLQ enqueue/pending/ready/discarded counters, shard depth gauges, and existing ingest pause counters now exposed.)*
- [x] Add structured logs with message IDs, conversation IDs, command names, and decision points (drops, retries, DLQ, pauses). *(Worker logging now binds message/conversation context, logs DLQ enqueues and command skips, and API client retries emit structured events; intake pauses remain logged with reasons.)*
- [x] Provide readiness/liveness endpoints and a CLI command to inspect health and DLQ status. *(New `HealthServer` exposes `/live`, `/ready`, `/dlq`; signal-ai CLI supports `--status` for health+DLQ inspection and can start the health server via `--health-host/--health-port`.)*

## Testing and tooling
- [ ] Ship fakes/mocks: in-memory websocket event source and fake REST clients to run handlers without a live Signal backend.
- [ ] Add contract tests for API parity against swagger (reuse `audit_api.py`) and for helper ergonomics (mentions, previews, media).
- [ ] Add load/saturation tests that verify backpressure, ordering guarantees, and DLQ replay under failure.

## Configuration and migration
- [ ] Document new config flags (durable queue, shard count, distributed locks, auth) with defaults and examples.
- [ ] Provide migration notes for any breaking changes (new models/events, typed responses).
- [ ] Maintain compatibility shim for legacy imports/functions; mark with deprecation warnings and dates.

## Documentation and examples
- [ ] Refresh README/quickstart with durable ingest setup, ordering guarantees, and new helpers.
- [ ] Add end-to-end examples: simple echo bot, media bot, group moderation bot with per-group limits, and a test harness example using fakes.
- [ ] Include operational runbook: how to start metrics server, inspect DLQ, pause/resume ingest, and interpret common errors.
