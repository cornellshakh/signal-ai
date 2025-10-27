import logging

from signalbot import Command, Context, triggered

log = logging.getLogger(__name__)


class HelloCommand(Command):
    def describe(self) -> str:
        return "Says hello."

    @triggered("hello")
    async def handle(self, c: Context) -> None:
        """Sends a hello message."""
        log.info("HelloCommand called")
        await c.send("Hello!")
