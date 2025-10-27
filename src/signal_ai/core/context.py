from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class Context(BaseModel):
    """
    Represents the context for a single chat.
    """
    chat_id: str
    mode: str = "normal"
    conversation_log: List[Dict[str, str]] = Field(default_factory=list)
    todo_list: List[str] = Field(default_factory=list)
    reminders: Dict[str, str] = Field(default_factory=dict)
