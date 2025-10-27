import logging
import os
import shlex
from typing import TYPE_CHECKING
from signalbot import Command, Context, regex_triggered

from .help import help_command_handler
from .config import config_command_handler
from .todo import todo_command_handler
from .remind import remind_command_handler

if TYPE_CHECKING:
    from ..bot import SignalAIBot

COMMANDS = {
    "help": help_command_handler,
    "config": config_command_handler,
    "todo": todo_command_handler,
    "remind": remind_command_handler,
}


class CommandDispatcher(Command):
    """
    A command that is triggered by a bot mention.
    It acts as a dispatcher for all other commands and natural language queries.
    """

    def describe(self) -> str:
        return "Handles all commands and conversations directed at the bot."

    @regex_triggered(r".*")
    async def handle(self, c: Context):
        """
        Parses the command and calls the appropriate handler.
        """
        if c.message.text is None:
            return

        bot_name = os.environ.get("BOT_NAME", "BotName")
        is_group_chat = c.message.group is not None
        text = c.message.text

        if not text:
            return

        if is_group_chat and not text.startswith(f"@{bot_name}"):
            return

        if TYPE_CHECKING:
            assert isinstance(c.bot, SignalAIBot)

        if c.bot.persistence_manager is None:
            return

        persistence_manager = c.bot.persistence_manager
        chat_context = persistence_manager.load_context(c.message.source)

        if not chat_context.welcomed:
            if is_group_chat:
                welcome_message = (
                    "Hello everyone. I am a helpful assistant.\n\n"
                    f"You can interact with me by mentioning my name, `@{bot_name}`.\n\n"
                    "To see a full list of what I can do, just type:\n"
                    f"`@{bot_name} help`"
                )
            else:
                welcome_message = (
                    "Hello! I am a helpful assistant.\n\n"
                    "To see a full list of what I can do, just type:\n"
                    "`help`"
                )
            await c.send(welcome_message, text_mode="styled")
            chat_context.welcomed = True
            persistence_manager.save_context(chat_context)
            return

        await c.start_typing()

        # Extract the text after the mention
        if is_group_chat:
            text_after_mention = text[len(bot_name) + 1 :].strip()
        else:
            text_after_mention = text.strip()

        if not text_after_mention:
            await c.send(
                "Hello! How can I help you? Type `@BotName help` for a list of commands.",
                text_mode="styled",
            )
            await c.stop_typing()
            return

        try:
            # Use shlex to handle quoted arguments
            parts = shlex.split(text_after_mention)
            command = parts[0].lower()
            args = parts[1:]
        except ValueError:
            await c.send(
                "⚠️ Error: Mismatched quotes in your command.", text_mode="styled"
            )
            await c.stop_typing()
            return

        handler = COMMANDS.get(command)
        if handler:
            logging.info(f"Handling command '{command}' with args: {args}")
            # Placeholder for reaction-based feedback
            # await c.react("⏳")
            await handler(c, args)
            # await c.react("✅")
        else:
            logging.info(f"Handling as natural language: '{text_after_mention}'")
            # Placeholder for Phase 5: AI Integration
            await c.send(
                "I'm not smart enough to have a conversation yet, but I will be soon!",
                text_mode="styled",
            )

        await c.stop_typing()
