from typing import Any, Optional

from signal_ai.core.command import BaseCommand, TextResult
from signal_ai.core.context import AppContext


class PingTool(BaseCommand):
    """
    A simple command to check if the bot is responsive.
    """

    @property
    def name(self) -> str:
        return "ping"

    @property
    def description(self) -> str:
        return "Checks if the bot is responsive."

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> TextResult:
        """
        Run the command.
        """
        return TextResult("pong")