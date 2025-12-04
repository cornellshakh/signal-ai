from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Iterable


def _parse_blocklist(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item for item in (part.strip() for part in raw.split(",")) if item}


@dataclass(slots=True)
class AppConfig:
    replay_dlq: bool
    metrics_host: str
    metrics_port: int
    health_host: str
    health_port: int
    health_timeout: float
    blocklist: set[str]
    faulty_contacts_base_url: str
    auto_start_signal_api: bool
    warm_api_session: bool
    start_metrics_server: bool
    start_health_server: bool
    status_only: bool
    secondary_member: str | None
    admin_number: str | None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="signal-ai bot")
    parser.add_argument(
        "--replay-dlq",
        action="store_true",
        help="Process eligible DLQ entries once and exit.",
    )
    parser.add_argument(
        "--metrics-host",
        default=os.environ.get("METRICS_HOST", "0.0.0.0"),
        help="Host for Prometheus metrics.",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=int(os.environ.get("METRICS_PORT", "9000")),
        help="Port for Prometheus metrics.",
    )
    parser.add_argument(
        "--health-host",
        default=os.environ.get("HEALTH_SERVER_HOST", "0.0.0.0"),
        help="Host for readiness/liveness server.",
    )
    parser.add_argument(
        "--health-port",
        type=int,
        default=int(os.environ.get("HEALTH_SERVER_PORT", "8081")),
        help="Port for readiness/liveness server.",
    )
    parser.add_argument(
        "--health-timeout",
        type=float,
        default=float(os.environ.get("HEALTH_TIMEOUT", "5.0")),
        help="Timeout for startup health checks.",
    )
    parser.add_argument(
        "--blocklist",
        default=os.environ.get("BLOCKLISTED", ""),
        help="Comma-separated list of numbers to block via middleware.",
    )
    parser.add_argument(
        "--faulty-contacts-base-url",
        default=os.environ.get("FAULT_BASE_URL", "http://127.0.0.1:9"),
        help="Base URL used when invoking '!contacts fault' to exercise retries.",
    )
    parser.add_argument(
        "--no-api-autostart",
        action="store_true",
        help="Skip auto-starting signal-cli-rest-api via scripts/manage_signal_api.py.",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Skip the initial HTTP warmup call to reduce first-command latency.",
    )
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Do not start the embedded Prometheus metrics server.",
    )
    parser.add_argument(
        "--no-health-server",
        action="store_true",
        help="Do not start the readiness/liveness server.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Inspect health and DLQ status then exit.",
    )
    parser.add_argument(
        "--secondary-member",
        default=os.environ.get("SECONDARY_MEMBER"),
        help="Optional second member used for group creation validation.",
    )
    parser.add_argument(
        "--admin-number",
        default=os.environ.get("ADMIN_NUMBER") or os.environ.get("SIGNAL_PHONE_NUMBER"),
        help="Phone number allowed to run '!admin'. Defaults to the bot number.",
    )
    return parser


def load_config(args: argparse.Namespace) -> AppConfig:
    return AppConfig(
        replay_dlq=bool(args.replay_dlq),
        metrics_host=str(args.metrics_host),
        metrics_port=int(args.metrics_port),
        health_host=str(args.health_host),
        health_port=int(args.health_port),
        health_timeout=float(args.health_timeout),
        blocklist=_parse_blocklist(args.blocklist),
        faulty_contacts_base_url=str(args.faulty_contacts_base_url),
        auto_start_signal_api=not bool(args.no_api_autostart),
        warm_api_session=not bool(args.no_warmup),
        start_metrics_server=not bool(args.no_metrics),
        start_health_server=not bool(args.no_health_server),
        status_only=bool(args.status),
        secondary_member=str(args.secondary_member) if args.secondary_member else None,
        admin_number=str(args.admin_number) if args.admin_number else None,
    )


def parse_args(argv: Iterable[str] | None = None) -> AppConfig:
    parser = build_arg_parser()
    return load_config(parser.parse_args(argv))
