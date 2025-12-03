# Signal Client Refactor Blueprint

Audience: a senior engineer who needs a concise blueprint for turning `signal-client` into a bot-friendly, ergonomic SDK instead of a thin REST wrapper.

## Objectives
- Align 1:1 with swagger, no dead endpoints (e.g., profiles are update-only, no GET).
- Prefer typed models over raw dicts for both requests and responses.
- Provide high-level helpers so bot authors focus on behavior, not payload shape.
- Bake resiliency (rate limit, circuit breaker, retries) and user-safe errors into the SDK.
- Ship examples, tests, and docs that mirror real bot flows.

## Immediate API Hygiene
- Run `scripts/audit_api.py` and fill gaps; remove or guard endpoints not in swagger.
- Fix schemas to match swagger: include all send fields (sticker, quote_mentions, view_once, notify_self, edit_timestamp, etc.), receipts, profile update (about/avatar), remote delete.
- Add response models where feasible (e.g., send response timestamp) instead of plain dicts.
- Add tests for every request/response shape you touch; use golden payloads to lock formatting.

## Ergonomic Context Helpers
- Expand `Context` with intent-level helpers:
  - `send_text`, `reply_text`, `send_markdown(text_mode="styled")`.
  - `send_sticker(pack_id, index)`; `send_view_once(attachments)`; `send_with_preview(url, title, description)`.
  - `reply_with_quote_mentions(text, mentions)` including a helper `mention_author()` to compute ranges safely.
  - `show_typing`/`hide_typing` wrappers that auto-target group vs DM.
  - `remote_delete(target_timestamp)` and `send_receipt(target_timestamp, type="read"|"viewed")`.
- Ensure helpers default recipients/number correctly and never require callers to fill `recipients=[]` manually.

## Command/Router Layer
- Enrich `@command` with optional guards and metadata: admin-only, group-only, throttling, usage text.
- Middleware catalog: blocklist, timing, retries/backoff, DLQ, panic-catcher.
- Auto-generated help/usage command from metadata.

## Errors & Resiliency
- Standardize an error type surfaced to callers (message, docs_url, status_code); avoid leaking raw exceptions.
- Wrap every API call with a built-in `safe_api_call` equivalent that logs and returns a typed result/None.
- Keep rate limiter and circuit breaker inside `BaseClient`; expose metrics hooks.

## Events & Storage
- Websocket client with reconnect/backoff; surface events beyond messages (receipts, typing indicators, reactions).
- Pluggable storage for message history and DLQ (SQLite/Redis). Provide an interface and default impls.

## Configuration & DI
- Single `Settings` source (env + overrides) used everywhere; document required vs optional fields.
- Factory to build clients/context with swap-in mocks for tests.

## Documentation & Examples
- Cookbook: sending text, mentions, link previews, view-once, stickers, receipts, typing, remote delete, sticker pack install.
- End-to-end sample bot showing routing, middleware, and helpers.
- Note API limitations explicitly (no message history REST endpoint, profiles update-only, etc.).

## Testing Strategy
- Unit tests for helpers (correct recipient defaulting, mention offsets, view-once flag).
- Golden tests for serialized requests per endpoint.
- Integration tests against a mocked REST server; optional contract test against swagger.

## Migration Notes
- Remove/replace `get_profile`; migrate callers to `update_profile` helper.
- Encourage use of new helpers instead of raw `SendMessageRequest` construction.
- Keep public APIs stable; add deprecation shims with warnings where needed.
