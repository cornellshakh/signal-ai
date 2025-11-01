from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from signal_ai.domain.context import AppContext
    from signal_ai.services.state import StateManager
    from signal_ai.infrastructure.ai import AIClient
    from signal_ai.infrastructure.signal import SignalTransport


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """

    name: str
    description: str
    schema: Type[BaseModel]

    @abstractmethod
    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        **kwargs: Any,
    ) -> str | None:
        """
        Executes the tool with the given context and arguments.
        """
        raise NotImplementedError