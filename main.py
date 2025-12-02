"""
A comprehensive test bot for the signal-client library.

This bot demonstrates the full range of features available in the signal-client,
acting as a live integration test and feature showcase.

Features demonstrated:
- Configuration overrides (resiliency, workers, storage)
- Middleware (timing, blocklisting)
- Advanced command routing (regex, whitelisting, case sensitivity)
- Context helpers (typing, reactions, attachments, mentions, locks)
- Direct API client usage (contacts, messages, groups)
- Observability (structured logging, Prometheus metrics)
- Dead-Letter Queue (DLQ) management
"""

from __future__ import annotations


import argparse
import asyncio
import base64
import os
import random
import re
import time
from collections.abc import Awaitable, Callable
from typing import Any


import structlog


from signal_client import Context, SignalClient


from signal_client.app import Application


from signal_client.command import command


from signal_client.config import Settings


from signal_client.infrastructure.schemas.groups import CreateGroupRequest


from signal_client.infrastructure.schemas.link_preview import LinkPreview


from signal_client.infrastructure.schemas.requests import SendMessageRequest


from signal_client.observability.logging import ensure_structlog_configured


from signal_client.observability.metrics import start_metrics_server


log = structlog.get_logger()


# ======================================================================================


# Configuration


# See: examples/config_resiliency_and_metrics.py


# ======================================================================================


# Override defaults without touching environment variables for secrets.


# This dictionary is passed directly to the SignalClient constructor.


CONFIG: dict[str, Any] = {
    # Backpressure and worker sizing.
    "queue_size": 200,
    "queue_put_timeout": 0.25,
    "queue_drop_oldest_on_timeout": False,  # fail fast instead of dropping.
    "worker_pool_size": 8,
    # API resiliency.
    "api_retries": 5,
    "api_backoff_factor": 0.75,
    "api_timeout": 20,
    "rate_limit": 20,
    "rate_limit_period": 1,
    "circuit_breaker_failure_threshold": 3,
    "circuit_breaker_reset_timeout": 10,
    # Storage swap (requires Redis reachable at provided host/port).
    # Uncomment the following lines to use Redis instead of SQLite.
    # "storage_type": "redis",
    # "redis_host": os.environ.get("REDIS_HOST", "localhost"),
    # "redis_port": int(os.environ.get("REDIS_PORT", "6379")),
    # DLQ configuration
    "dlq_name": "signal-ai-dlq",
    "dlq_max_retries": 3,
}


# ======================================================================================


# Shared State


# ======================================================================================


# In-memory balance tracking for the `!balance` command.


# NOTE: This is for demonstration only. In a real application, this should


# be persisted in a database.


_balances: dict[str, int] = {}





# Help text, generated dynamically on startup.


HELP_TEXT = "Help text not available."


# ======================================================================================


# Middleware


# See: examples/routing_and_middleware.py


# ======================================================================================


async def timing_middleware(
    ctx: Context, next_callable: Callable[[Context], Awaitable[None]]
) -> None:
    """Logs the execution time of each command."""

    started = time.perf_counter()

    await next_callable(ctx)

    elapsed_ms = (time.perf_counter() - started) * 1000

    log.info("command.timing", command=ctx.message.message, elapsed_ms=elapsed_ms)


async def blocklist_middleware(
    ctx: Context, next_callable: Callable[[Context], Awaitable[None]]
) -> None:
    """Prevents users on a blocklist from executing commands."""

    # This is a simple example. A real implementation might use a database.

    blocklisted = {os.environ.get("BLOCKED_NUMBER", "+19998887777")}

    if ctx.message.source in blocklisted:

        log.warn("command.blocked", source=ctx.message.source)

        return  # Stop processing for this user.

    await next_callable(ctx)


# ======================================================================================


# Commands


# See: examples/*.py


# ======================================================================================


@command("!ping")
async def ping(ctx: Context) -> None:
    """A basic command to check if the bot is alive."""

    await ctx.reply(SendMessageRequest(message="pong", recipients=[ctx.message.source]))


# @command("!settings")
# async def settings_echo(ctx: Context) -> None:
#     """Replies with some of the custom settings to show they are active."""
#     # TODO: This command is disabled because ctx.app is not a valid attribute.
#     # A different way to access app settings from a command context is needed.
#     await ctx.reply(
#         SendMessageRequest(
#             message=(
#                 "Custom settings active: "
#                 f"workers={ctx.app.settings.worker_pool_size}, "
#                 f"queue={ctx.app.settings.queue_size}, "
#                 f"retries={ctx.app.settings.api_retries}"
#             ),
#             recipients=[ctx.message.source],
#         )
#     )


@command("!echo")
async def echo(ctx: Context) -> None:
    """Demonstrates typing indicators."""

    await ctx.start_typing()

    try:

        text = ctx.message.message or ""

        await asyncio.sleep(1)  # Simulate work

        await ctx.reply(
            SendMessageRequest(message=f"echo: {text}", recipients=[ctx.message.source])
        )

    finally:

        await ctx.stop_typing()


@command("!react")
async def react(ctx: Context) -> None:
    """Demonstrates adding and removing reactions."""

    await ctx.react("👍")

    await asyncio.sleep(2)

    await ctx.remove_reaction()


@command("!share")
async def share(ctx: Context) -> None:
    """Demonstrates sending attachments, mentions, and link previews."""

    attachment = base64.b64encode(b"hello from signal-client").decode()

    mention = {
        "number": ctx.message.source,
        "length": 1,
        "offset": 0,
    }

    preview = LinkPreview(
        url="https://github.com/filip-zy/signal-client",
        title="signal-client",
        description="A Python library for building Signal bots.",
    )

    payload = SendMessageRequest(
        recipients=[ctx.message.source],
        message="@ mentioned you and sent an attachment with a preview!",
        base64_attachments=[attachment],
        mentions=[mention],
        preview=preview,
    )

    await ctx.send(payload)


@command("!balance")
async def balance(ctx: Context) -> None:
    """Demonstrates async locks for safe concurrent state updates."""

    user = ctx.message.source

    # Use a lock to prevent race conditions if multiple messages arrive at once.

    async with ctx.lock(f"balance:{user}"):

        current = _balances.get(user, 100)

        await asyncio.sleep(0.5)  # Simulate a slow operation

        _balances[user] = current + 10

        await ctx.reply(
            SendMessageRequest(
                message=f"Balance for {user}: {_balances[user]}",
                recipients=[ctx.message.source],
            )
        )


@command(re.compile(r"!roll\s+(\d+)d(\d+)", re.IGNORECASE))
async def dice(ctx: Context) -> None:
    """Demonstrates a regex-triggered command."""

    match = re.search(r"!roll\s+(\d+)d(\d+)", ctx.message.message or "", re.IGNORECASE)

    if not match:

        return

    count, sides = (int(match.group(1)), int(match.group(2)))

    rolls = [random.randint(1, sides) for _ in range(count)]
    await ctx.reply(
        SendMessageRequest(
            message=f"Rolled {count}d{sides}: {rolls} (total={sum(rolls)})",
            recipients=[ctx.message.source],
        )
    )


@command(
    "!ADMIN",
    whitelisted=[os.environ.get("ADMIN_NUMBER", "+1234567890")],
    case_sensitive=True,
)
async def admin_only(ctx: Context) -> None:
    """Demonstrates a whitelisted, case-sensitive command."""

    await ctx.reply(
        SendMessageRequest(
            message="Admin command executed successfully.",
            recipients=[ctx.message.source],
        )
    )


@command("!contacts")
async def list_contacts(ctx: Context) -> None:
    """Demonstrates direct API client usage for contacts."""

    me = ctx._phone_number  # Provided via ContextDependencies.

    contacts = await ctx.contacts.get_contacts(me)

    await ctx.reply(
        SendMessageRequest(
            message=f"Found {len(contacts)} contacts in my list.",
            recipients=[ctx.message.source],
        )
    )


@command("!history")
async def last_messages(ctx: Context) -> None:
    """Demonstrates direct API client usage for messages."""

    me = ctx._phone_number

    history = await ctx.messages.get_messages(me, ctx.message.source, limit=5)

    snippets = [item.get("message") for item in history if item.get("message")]

    await ctx.reply(
        SendMessageRequest(
            message="Recent messages:\n" + "\n".join(snippets),
            recipients=[ctx.message.source],
        )
    )


@command("!newgroup")
async def create_group(ctx: Context) -> None:
    """Demonstrates direct API client usage for groups."""

    me = ctx._phone_number

    # Create a group with the sender and another member (from env or sender again).

    members = [
        ctx.message.source,
        os.environ.get("SECONDARY_MEMBER", ctx.message.source),
    ]

    request = CreateGroupRequest(name="signal-client test group", members=members)

    group = await ctx.groups.create_group(me, request)

    await ctx.reply(
        SendMessageRequest(
            message=f"Created group {group.get('id', '<unknown>')}",
            recipients=[ctx.message.source],
        )
    )


@command("!help")
async def help_command(ctx: Context) -> None:
    """Displays information about available commands."""
    await ctx.reply(
        SendMessageRequest(message=HELP_TEXT, recipients=[ctx.message.source])
    )


def register_commands(bot: SignalClient) -> None:
    """Registers all commands with the bot."""
    global HELP_TEXT

    # Create a list of all command objects to register.
    # The @command decorator returns a Command object, so we can inspect it.
    commands_to_register = [
        ping,
        echo,
        react,
        share,
        balance,
        dice,
        admin_only,
        list_contacts,
        last_messages,
        create_group,
        help_command,
    ]

    # Register all commands with the bot.
    for cmd in commands_to_register:
        bot.register(cmd)

    # --- Generate HELP_TEXT from the manual list ---
    help_message_lines = ["Available commands:"]
    for cmd_obj in sorted(commands_to_register, key=lambda c: str(c.name)):
        # The name can be a string or a regex pattern.
        name = cmd_obj.name
        if not hasattr(cmd_obj, "func") or not cmd_obj.func.__doc__:
            continue

        description = str(cmd_obj.func.__doc__.strip().splitlines()[0])
        help_message_lines.append(f"- `{name}`: {description}")

    HELP_TEXT = "\n".join(help_message_lines)


# ======================================================================================


# Application Entry Points


# ======================================================================================


async def run_bot() -> None:
    """Initializes and runs the bot."""

    # The SignalClient constructor can take a config dict, a path to a config

    # file, or use environment variables.

    async with SignalClient(config=CONFIG) as bot:

        # Middleware is executed in the order it's added.

        bot.use(timing_middleware)

        bot.use(blocklist_middleware)

        # Register all the commands defined above.

        register_commands(bot)

        log.info("Bot starting...")

        await bot.start()


async def replay_dlq() -> None:
    """Initializes the application and replays messages from the DLQ."""

    log.info("Attempting to replay DLQ...")

    settings = Settings.from_sources(CONFIG)

    app = Application(settings)

    await app.initialize()

    if app.dead_letter_queue is None:

        log.error("DLQ not configured. Cannot replay.")

        raise RuntimeError("DLQ not configured.")

    replayed_count = await app.dead_letter_queue.replay()

    log.info(f"Replayed {replayed_count} messages from the DLQ.")

    await app.shutdown()


def _get_parser() -> argparse.ArgumentParser:
    """Creates and returns the argument parser."""

    parser = argparse.ArgumentParser(
        description="A comprehensive test bot for signal-client."
    )

    parser.add_argument(
        "--replay-dlq",
        action="store_true",
        help="Process eligible messages from the dead-letter queue once and exit.",
    )

    return parser


if __name__ == "__main__":

    # Configure logging and metrics.

    ensure_structlog_configured()

    start_metrics_server(
        port=int(os.getenv("METRICS_PORT", "9000")),
        addr=os.getenv("METRICS_HOST", "0.0.0.0"),
    )

    # Parse command-line arguments to decide the mode of operation.

    args = _get_parser().parse_args()

    loop = asyncio.get_event_loop()

    try:

        if args.replay_dlq:

            loop.run_until_complete(replay_dlq())

        else:

            loop.run_until_complete(run_bot())

    except KeyboardInterrupt:

        log.info("Caught KeyboardInterrupt, shutting down.")

    finally:

        loop.close()
