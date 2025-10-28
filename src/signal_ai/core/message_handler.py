import os
import shlex
import structlog
from typing import TYPE_CHECKING, cast
from signalbot import Command, Context, regex_triggered
from ..commands.help import handle_help
from ..commands.config import handle_config
from ..commands.todo import handle_todo
from ..commands.remind import handle_remind
from ..commands.search import handle_search
from ..commands.image import handle_image

if TYPE_CHECKING:
    from signal_ai.bot import SignalAIBot


log = structlog.get_logger()


class MessageHandler(Command):
    """
    Centralized handler for all incoming messages.
    This class implements the Interaction Logic Gate and routes messages.
    """

    def describe(self) -> str:
        return "Handles all incoming messages and routes them appropriately."

    @regex_triggered(r".*")
    async def handle(self, c: Context):
        """
        The main entry point for processing messages.
        """
        if c.message.text is None:
            return

        bot_name = os.environ.get("BOT_NAME", "BotName")
        is_group_chat = c.message.group is not None
        text = c.message.text.strip()

        if not text:
            return

        # Interaction Logic Gate
        if is_group_chat and not text.startswith(f"@{bot_name}"):
            # In group chats, only respond to mentions
            return

        bot = cast("SignalAIBot", c.bot)

        if bot.persistence_manager is None:
            log.error("persistence_manager_not_initialized")
            return

        chat_context = bot.persistence_manager.load_context(c.message.source)

        # Don't respond if mode is 'quiet'
        if chat_context.config.mode == "quiet":
            log.info(
                "quiet_mode_enabled",
                chat_source=c.message.source,
            )
            return

        await c.react("⏳")
        await c.start_typing()

        # Message Parsing and Routing
        try:
            if is_group_chat:
                text_after_mention = text[len(bot_name) + 1 :].strip()
            else:
                text_after_mention = text

            if not text_after_mention:
                # The bot was just mentioned with no command
                await self._reply(
                    c,
                    f"Hello! How can I help you? Type `@{bot_name} !help` for commands.",
                )
                await c.stop_typing()
                await c.react("✅")
                return

            if text_after_mention.startswith("!"):
                # This is a command
                await self._handle_command(c, text_after_mention)
            else:
                # This is a conversational message for the AI
                await self._handle_ai_query(c, text_after_mention)

            await c.stop_typing()
            await c.react("✅")
        except Exception as e:
            log.error("message_handling_error", error=str(e))
            await self._reply(
                c,
                "An unexpected error occurred. I've logged the issue for my developer to review.",
            )
            await c.stop_typing()
            await c.react("❌")

    async def _handle_command(self, c: Context, text: str):
        """
        Parses and dispatches a `!` command.
        """
        bot = cast("SignalAIBot", c.bot)
        try:
            parts = shlex.split(text)
            command_name = parts[0][1:].lower()  # Remove '!'
            args = parts[1:]
        except ValueError:
            await self._reply(c, "⚠️ Error: Mismatched quotes in your command.")
            return

        log.info("handling_command", command_name=command_name, args=args)

        if command_name == "help":
            # Pass bot_name as an argument to handle_help
            bot_name = os.environ.get("BOT_NAME", "BotName")
            await handle_help(c, [bot_name] + args)
        elif command_name == "config":
            if bot.persistence_manager:
                await handle_config(c, args, bot.persistence_manager)
        elif command_name == "todo":
            if bot.persistence_manager:
                await handle_todo(c, args, bot.persistence_manager)
        elif command_name == "remind":
            if bot.scheduler:
                await handle_remind(c, args, bot.scheduler)
        elif command_name == "search":
            if bot.ai_client:
                await handle_search(c, args, bot.ai_client)
        elif command_name == "image":
            if bot.ai_client:
                await handle_image(c, args, bot.ai_client)
        else:
            # Placeholder for other command handling logic
            await self._reply(c, f"Unknown command: `{command_name}`.")

    async def _handle_ai_query(self, c: Context, text: str):
        """
        Handles a natural language query meant for the AI.
        """
        log.info("handling_ai_query", query=text)

        bot = cast("SignalAIBot", c.bot)

        if bot.ai_client:
            response = await bot.ai_client.generate_response(text)
            await self._reply(c, response)
        else:
            await self._reply(
                c,
                "AI client not configured. Please set the GEMINI_API_KEY environment variable.",
            )

    async def _reply(self, c: Context, message: str):
        """
        Sends a reply to the user, using a direct reply in DMs
        and a mention-reply in group chats.
        """
        await c.reply(message)
