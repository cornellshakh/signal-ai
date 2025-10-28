from signalbot import Command, Context, triggered


class PingCommand(Command):
    def describe(self) -> str:
        return "A simple command to check if the bot is responsive."

    @triggered("!system ping")
    async def handle(self, c: Context) -> None:
        await c.send("pong", text_mode="styled")
