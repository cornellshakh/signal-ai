from __future__ import annotations

from dataclasses import dataclass, field

from signal_client.command import Command

CommandHandler = Command


@dataclass(slots=True)
class CommandOptions:
    admin_number: str | None
    faulty_contacts_base_url: str
    secondary_member: str | None


@dataclass(slots=True)
class BotState:
    balances: dict[str, int] = field(default_factory=dict)
