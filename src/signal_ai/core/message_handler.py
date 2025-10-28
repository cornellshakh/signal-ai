import os
import re
import shlex
import structlog
from typing import TYPE_CHECKING, cast
from signalbot import Command, Context, regex_triggered

if TYPE_CHECKING:
    from signal_ai.bot import SignalAIBot


HISTORY_WINDOW_SIZE = 4
log = structlog.get_logger()


def cleanup_signal_formatting(text: str) -> str:
    """
    Cleans up AI-generated text for a better chat experience in Signal.
    """
    # Convert multi-line code blocks to monospaced text within spoilers.
    text = re.sub(r"```(?:\w+\n)?(.*?)```", r"||\`\1`||", text, flags=re.DOTALL)

    # Ensure consistent list formatting
    text = re.sub(r"^\s*\*\s+", "- ", text, flags=re.MULTILINE)

    # Remove leading/trailing whitespace.
    text = text.strip()

    # Collapse more than two consecutive newlines into a maximum of two.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove newlines between list items and other formatted lines
    text = re.sub(r"(\n- .*\n)\n", r"\1", text)
    text = re.sub(r"(\n\d+\..*\n)\n", r"\1", text)
    text = re.sub(r"(\n\*[^*]+\*.*\n)\n", r"\1", text)


    return text


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
        if not c.message or c.message.text is None:
            return

        # Bind key message info to the logging context for this request
        structlog.contextvars.bind_contextvars(
            source_uuid=c.message.source_uuid,
            source_number=c.message.source_number,
            timestamp=c.message.timestamp,
        )

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
            log.error("persistence_manager.not_initialized")
            return

        chat_context = bot.persistence_manager.load_context(c.message.source)

        # Don't respond if mode is 'quiet'
        if chat_context.config.mode == "quiet":
            log.info(
                "bot.quiet_mode_enabled",
                chat_source=c.message.source,
            )
            return

        # Message Parsing and Routing
        try:
            await c.react("⏳")
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
                await c.react("⚛️")
                return

            if not text_after_mention.startswith("!"):
                # This is a conversational message for the AI
                await self._handle_ai_query(c, text_after_mention)

            await c.react("⚛️")
        except Exception as e:
            log.error("message.handle.failed", error=str(e))
            await self._reply(
                c,
                "An unexpected error occurred. I've logged the issue for my developer to review.",
            )
            await c.react("❌")

    async def _handle_ai_query(self, c: Context, text: str):
        """
        Handles a natural language query meant for the AI.
        """
        log.info("ai_query.received", query=text)

        bot = cast("SignalAIBot", c.bot)

        if bot.ai_client and bot.persistence_manager:
            chat_context = bot.persistence_manager.load_context(c.message.source)

            # Implement the sliding window for history
            if len(chat_context.history) > HISTORY_WINDOW_SIZE:
                chat_context.history = chat_context.history[-HISTORY_WINDOW_SIZE:]

            # Prepare the history for the AI
            ai_history = chat_context.history

            response = await bot.ai_client.generate_response(
                chat_id=c.message.source,
                prompt=text,
                history=ai_history,
            )

            # Update history
            chat_context.history.append({"role": "user", "parts": [text]})
            chat_context.history.append({"role": "model", "parts": [response]})
            bot.persistence_manager.save_context(c.message.source)

            # Apply final cleanup
            final_response = cleanup_signal_formatting(response)
            await self._reply(c, final_response)
        else:
            await self._reply(
                c,
                "AI client or persistence manager not configured.",
            )

    async def _reply(self, c: Context, message: str):
        """
        Sends a reply to the user, using a direct reply in DMs
        and a mention-reply in group chats.
        """
        await c.reply(message, text_mode="styled")
