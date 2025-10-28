from typing import List
from signalbot import Context
from ...core.command import BaseCommand


class PingCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "ping"

    @property
    def description(self) -> str:
        return "A simple command to check if the bot is responsive."

    async def handle(self, c: Context, args: List[str]) -> None:
        await c.send("pong", text_mode="styled")
