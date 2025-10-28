from typing import List, Dict, Any
from pydantic import BaseModel, Field


class BotConfig(BaseModel):
    """Bot configuration settings."""

    mode: str = Field(default="ai", description="The interaction mode of the bot.")


class Context(BaseModel):
    """Represents the context of a single chat."""

    config: BotConfig = Field(default_factory=BotConfig)
    pinned_message: str = Field(default="", description="A pinned message for core context.")
    history: List[Dict[str, Any]] = Field(default_factory=list)
    todos: List[str] = Field(default_factory=list)
