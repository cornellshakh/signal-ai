from typing import Any, List
from google.generativeai.types import ContentDict
from pydantic import BaseModel, Field


class ChatConfig(BaseModel):
    mode: str = "ai"


class AppContext(BaseModel):
    """
    Represents the context of a single chat session.
    """

    model_config = {"arbitrary_types_allowed": True}

    # Message Data
    message: dict[str, Any] | None = None

    # State Data
    chat_id: str
    pinned_message: str = ""
    chat_history: List[ContentDict] = Field(default_factory=list)
    config: ChatConfig = Field(default_factory=ChatConfig)
    todos: list[str] = Field(default_factory=list)