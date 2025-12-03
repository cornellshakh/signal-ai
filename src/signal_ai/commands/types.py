from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable

from signal_client import Context

CommandHandler = Callable[[Context], Awaitable[None]]


@dataclass(slots=True)
class CommandOptions:
    admin_number: str | None
    faulty_contacts_base_url: str
    secondary_member: str | None


@dataclass(slots=True)
class BotState:
    balances: dict[str, int] = field(default_factory=dict)
