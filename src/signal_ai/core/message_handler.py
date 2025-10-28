import asyncio
import os
import re
import shlex
import time
import structlog
from typing import TYPE_CHECKING, cast, Optional
from signalbot import Context, Message, SendMessageError

if TYPE_CHECKING:
    from ..bot import SignalAIBot


HISTORY_WINDOW_SIZE = 50
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

    # Trim dangling markdown formatting characters from the start and end of the text
    formatting_chars = r"\*|_|~|`|\|"
    text = re.sub(rf"^({formatting_chars})+", "", text)
    text = re.sub(rf"({formatting_chars})+$", "", text)

    return text


from .dispatcher import CommandDispatcher


class MessageHandler:
    """
    Centralized handler for all incoming messages.
    This class implements the Interaction Logic Gate and routes messages.
    """

    def __init__(self, dispatcher: CommandDispatcher):
        self.dispatcher = dispatcher

    async def handle(self, c: Context):
        """
        The main entry point for processing messages.
        This method now creates a background task to handle the message asynchronously.
        """
        if not c.message or c.message.text is None:
            return

        # We are creating a task to process the message in the background.
        # This allows the bot to quickly acknowledge the message and be ready for the next one.
        asyncio.create_task(self._process_message_async(c))

    async def _process_message_async(self, c: Context):
        """
        The actual message processing logic, run as a background task.
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
        bot = cast("SignalAIBot", c.bot)
        if bot.persistence_manager is None:
            log.error("persistence_manager.not_initialized")
            return
        
        chat_context = bot.persistence_manager.load_context(c.message.source)

        if is_group_chat and not chat_context.is_initialized:
            chat_context.config.mode = "mention"
            chat_context.is_initialized = True

        if is_group_chat and chat_context.config.mode == "mention" and not text.startswith(f"@{bot_name}"):
            return

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

            if text_after_mention.startswith("!"):
                await self.dispatcher.dispatch(c, text_after_mention)
            else:
                # This is a conversational message for the AI
                await self._handle_ai_query_stream(c, text_after_mention)

            await c.react("⚛️")
        except Exception as e:
            log.error("message.handle.failed", error=str(e), exc_info=True)
            await self._reply(
                c,
                "An unexpected error occurred while processing your message. The issue has been logged.",
            )
            await c.react("❌")

    async def _handle_ai_query_stream(self, c: Context, text: str):
        """
        Handles a natural language query meant for the AI, with streaming.
        """
        log.info("ai_query.received", query=text)

        bot = cast("SignalAIBot", c.bot)

        if not bot.ai_client or not bot.persistence_manager:
            await self._reply(c, "AI client or persistence manager not configured.")
            return

        chat_context = bot.persistence_manager.load_context(c.message.source)

        # Implement the sliding window for history
        if len(chat_context.history) > HISTORY_WINDOW_SIZE:
            chat_context.history = chat_context.history[-HISTORY_WINDOW_SIZE:]

        ai_history = chat_context.history

        # Prepare for streaming
        full_response = ""
        sent_message_timestamp: Optional[int] = None
        last_update_time = 0
        UPDATE_INTERVAL = 0.5  # seconds

        try:
            thinking_message_timestamp = await c.reply("Thinking...")
            stream = bot.ai_client.generate_response_stream(
                chat_id=c.message.source, prompt=text, history=ai_history
            )

            async for chunk in stream:
                full_response += chunk
                current_time = time.time()
                cleaned_response = cleanup_signal_formatting(full_response)

                if not cleaned_response or not cleaned_response.strip():
                    continue

                try:
                    if sent_message_timestamp is None:
                        await c.edit(
                            cleaned_response,
                            edit_timestamp=thinking_message_timestamp,
                            text_mode="styled",
                        )
                        sent_message_timestamp = thinking_message_timestamp
                        last_update_time = current_time
                    elif current_time - last_update_time > UPDATE_INTERVAL:
                        await c.edit(
                            cleaned_response,
                            edit_timestamp=sent_message_timestamp,
                            text_mode="styled",
                        )
                        last_update_time = current_time
                except SendMessageError:
                    log.warning(
                        "ai_query_stream.send.failed",
                        text=cleaned_response,
                        exc_info=True,
                    )

            if sent_message_timestamp:
                final_cleaned_response = cleanup_signal_formatting(full_response)
                if final_cleaned_response and final_cleaned_response.strip():
                    try:
                        await c.edit(
                            final_cleaned_response,
                            edit_timestamp=sent_message_timestamp,
                            text_mode="styled",
                        )
                    except SendMessageError:
                        log.error(
                            "ai_query_stream.final_send.failed",
                            text=final_cleaned_response,
                            exc_info=True,
                        )

            chat_context.history.append({"role": "user", "parts": [text]})
            chat_context.history.append({"role": "model", "parts": [full_response]})
            bot.persistence_manager.save_context(c.message.source)

        except Exception as e:
            log.error("ai_query_stream.failed", error=str(e), exc_info=True)
            await self._reply(c, "An error occurred while streaming the AI response.")
            await c.react("❌")

    async def _reply(self, c: Context, message: str):
        """
        Sends a reply to the user, using a direct reply in DMs
        and a mention-reply in group chats.
        """
        await c.reply(message, text_mode="styled")
