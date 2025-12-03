"""Manage the bbernhard/signal-cli-rest-api container.

Supports start/stop/restart/status with the same defaults as start_signal_api.py.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, check=False, capture_output=True)


def _docker_available() -> bool:
    result = _run(["docker", "version", "--format", "{{.Server.Version}}"])
    return result.returncode == 0


def _container_status(name: str) -> str | None:
    result = _run(["docker", "inspect", "-f", "{{.State.Status}}", name])
    if result.returncode != 0:
        return None
    return result.stdout.decode().strip()


def _start_existing(name: str) -> bool:
    result = _run(["docker", "start", name])
    return result.returncode == 0


def _ensure_data_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _run_new_container(
    name: str, port: int, mode: str, image: str, data_dir: Path
) -> bool:
    _ensure_data_dir(data_dir)
    cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        name,
        "--restart=always",
        "-p",
        f"{port}:8080",
        "-v",
        f"{data_dir}:/home/.local/share/signal-cli",
        "-e",
        f"MODE={mode}",
        image,
    ]
    result = _run(cmd)
    return result.returncode == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage bbernhard/signal-cli-rest-api container",
    )
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "--name",
        default=os.environ.get("SIGNAL_API_CONTAINER", "signal-api"),
        help="Docker container name.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SIGNAL_API_PORT", "8080")),
        help="Host port to expose (maps to container 8080).",
    )
    parser.add_argument(
        "--mode",
        default=os.environ.get("SIGNAL_API_MODE", "native"),
        help="signal-cli-rest-api MODE env (default native for low-latency websocket receive).",
    )
    parser.add_argument(
        "--image",
        default=os.environ.get(
            "SIGNAL_API_IMAGE", "bbernhard/signal-cli-rest-api:0.95"
        ),
        help="Docker image to use.",
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get(
            "SIGNAL_API_DATA_DIR", os.path.expanduser("~/.local/share/signal-api")
        ),
        help="Host directory for signal-cli state (mounted into container).",
    )
    return parser.parse_args()


def _stop_container(name: str) -> bool:
    result = _run(["docker", "stop", name])
    return result.returncode == 0


def main() -> int:
    args = parse_args()
    if not _docker_available():
        print("Docker is not available. Please install/start Docker.", file=sys.stderr)
        return 1

    status = _container_status(args.name)

    if args.command == "status":
        print(status or "absent")
        return 0 if status else 1

    if args.command == "stop":
        if status is None:
            print(f"Container {args.name} not found.")
            return 1
        if status == "exited":
            print(f"Container {args.name} already stopped.")
            return 0
        if _stop_container(args.name):
            print(f"Stopped {args.name}.")
            return 0
        print(f"Failed to stop {args.name}.", file=sys.stderr)
        return 1

    if args.command == "start":
        if status == "running":
            print(f"{args.name} already running on port {args.port}.")
            return 0
        if status in {"exited", "created"}:
            if _start_existing(args.name):
                print(f"Started existing container {args.name}.")
                return 0
            print(f"Failed to start existing container {args.name}.", file=sys.stderr)
            return 1

        data_dir = Path(args.data_dir).expanduser()
        if _run_new_container(args.name, args.port, args.mode, args.image, data_dir):
            print(
                f"Started {args.name} ({args.image}) mode={args.mode} port={args.port} data_dir={data_dir}"
            )
            return 0

        print(f"Failed to run container {args.name}.", file=sys.stderr)
        return 1

    if args.command == "restart":
        if status:
            _stop_container(args.name)
        data_dir = Path(args.data_dir).expanduser()
        # If container exists, try start; else run new.
        status_after_stop = _container_status(args.name)
        if status_after_stop in {"exited", "created", "running"}:
            if _start_existing(args.name):
                print(f"Restarted existing container {args.name}.")
                return 0
        if _run_new_container(args.name, args.port, args.mode, args.image, data_dir):
            print(
                f"Started {args.name} ({args.image}) mode={args.mode} port={args.port} data_dir={data_dir}"
            )
            return 0
        print(f"Failed to restart {args.name}.", file=sys.stderr)
        return 1

    print(f"Unknown command {args.command}.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
