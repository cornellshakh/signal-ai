import asyncio
import random

from signalbot import Command, Context, triggered


class TypingCommand(Command):
    def describe(self) -> str:
        return "A command to demonstrate the typing indicator."

    @triggered("typing")
    async def handle(self, c: Context) -> None:
        seconds = random.randint(1, 5)  # noqa: S311
        await c.start_typing()
        await asyncio.sleep(seconds)
        await c.stop_typing()
        await c.send(f"Typed for {seconds}s", text_mode="styled")
