from typing import List, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field
from signalbot.context import Context as SignalBotContext

if TYPE_CHECKING:
    from .persistence import PersistenceManager


class BotConfig(BaseModel):
    """Bot configuration settings."""

    mode: str = Field(default="ai", description="The interaction mode of the bot.")


class Context(BaseModel):
    """Represents the persistent context of a single chat."""

    config: BotConfig = Field(default_factory=BotConfig)
    pinned_message: str = Field(
        default="", description="A pinned message for core context."
    )
    history: List[Dict[str, Any]] = Field(default_factory=list)
    todos: List[str] = Field(default_factory=list)
    is_initialized: bool = Field(
        default=False, description="Whether the context has been initialized."
    )


class AppContext(BaseModel):
    """
    Represents the platform-agnostic context for a single incoming message.
    This is the primary data structure for the new architecture.
    """

    chat_id: str
    sender_id: str
    message_text: str
    persistent_context: Context
    raw_context: SignalBotContext

    class Config:
        arbitrary_types_allowed = True

    async def reply(self, text: str, **kwargs):
        await self.raw_context.reply(text, **kwargs)


async def to_app_context(
    context: SignalBotContext, persistence_manager: "PersistenceManager"
) -> AppContext:
    """
    Adapter function to convert a signalbot.Context to an AppContext.

    Args:
        context: The original context from the signalbot library.
        persistence_manager: The application's persistence manager.

    Returns:
        An AppContext instance.
    """
    chat_id = context.message.source
    sender_id = context.message.source
    message_text = context.message.text

    persistent_context = await persistence_manager.load_context(chat_id)

    return AppContext(
        chat_id=chat_id,
        sender_id=sender_id,
        message_text=message_text,
        persistent_context=persistent_context,
        raw_context=context,
    )
