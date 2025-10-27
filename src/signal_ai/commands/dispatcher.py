import logging
from signalbot import Command, Context, regex_triggered

async def help_command_handler(context: Context):
    """
    Handles the 'help' command.
    """
    help_text = """
Available commands:
- !help: Show this help message.
- !config: View or set configuration.
- !todo: Manage your to-do list.
- !remind: Set a reminder.
- !search: Search the web.
- !image: Generate an image.
"""
    await context.send(help_text)

COMMANDS = {
    "help": help_command_handler,
}

class CommandDispatcher(Command):
    """
    A command that is triggered by a command prefix.
    It acts as a dispatcher for other commands.
    """
    def describe(self) -> str:
        return "Handles all commands starting with a '!' prefix."

    @regex_triggered(r"^!(\w+)")
    async def handle(self, c: Context):
        """
        Parses the command and calls the appropriate handler.
        """
        if not c.message.text:
            return

        # Simple parser: command is the first word after the prefix
        command = c.message.text.strip()[1:].split()[0].lower()
        # args = c.message.text.strip().split()[1:] # Will be used later

        handler = COMMANDS.get(command)
        if handler:
            await handler(c)
        else:
            await c.send(f"Unknown command: '{command}'. Type '!help' for a list of commands.")
