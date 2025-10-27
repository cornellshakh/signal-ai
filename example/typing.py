import asyncio

from signalbot import Command, Context, triggered


class TypingCommand(Command):
    def describe(self) -> str:
        return "A command to demonstrate the typing indicator."

    @triggered("typing")
    async def handle(self, c: Context) -> None:
        await c.start_typing()
        seconds = 5
        await asyncio.sleep(seconds)
        await c.stop_typing()
        await c.send(f"Typed for {seconds}s")
