from typing import Any, Optional, Union

from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class PingCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "ping"

    @property
    def description(self) -> str:
        return "Checks if the bot is responsive."

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        return TextResult("pong")