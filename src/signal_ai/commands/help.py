from signalbot import Command, Context


class HelpCommand(Command):
    def describe(self) -> str:
        return "!help - Show this help message"

    async def handle(self, c: Context):
        help_text = """
Available commands:
- !ping: Check if the bot is alive.
- !reply: Reply to the message.
- !attachment: Send an attachment.
- !trigger: A triggered command.
- !edit: Edit a message.
- !delete: Delete a message.
- !styles: Show different text styles.
- !search: Search the web.
- !convert: Convert units.
- !hello: Say hello.
- !help: Show this help message.
"""
        await c.send(help_text)
