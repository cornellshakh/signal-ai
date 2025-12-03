from __future__ import annotations

from typing import Iterable

from .admin import build_admin_command
from .balance import build_balance_command
from .contacts import build_contacts_command
from .dlq_fail import build_dlq_fail_command
from .echo import build_echo_command
from .history import build_history_command
from .newgroup import build_new_group_command
from .ping import build_ping_command
from .react import build_react_command
from .roll import build_roll_command
from .settings import build_settings_command
from .share import build_share_command
from .types import BotState, CommandHandler, CommandOptions

__all__ = [
    "BotState",
    "CommandOptions",
    "CommandHandler",
    "build_command_handlers",
]


def build_command_handlers(options: CommandOptions) -> Iterable[CommandHandler]:
    state = BotState()
    return [
        build_ping_command(),
        build_settings_command(),
        build_echo_command(),
        build_react_command(),
        build_share_command(),
        build_balance_command(state),
        build_roll_command(),
        build_admin_command(options),
        build_contacts_command(options),
        build_history_command(),
        build_new_group_command(options),
        build_dlq_fail_command(),
    ]
