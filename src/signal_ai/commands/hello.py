import logging

from signalbot import Command, Context, triggered

log = logging.getLogger(__name__)


class HelloCommand(Command):
    def describe(self) -> str:
        return "Says hello."

    @triggered("hello")
    async def handle(self, c: Context) -> None:
        await c.send("Hello!", text_mode="styled")
        log.info("HelloCommand called")
        await c.send("Hello!", text_mode="styled")
