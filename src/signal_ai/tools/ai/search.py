from typing import Any

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.state import StateManager


class SearchSchema(BaseModel):
    query: str = Field(..., description="The query to search for.")


class SearchTool(BaseTool):
    """
    Searches the web and summarizes the results.
    """

    name = "search"
    description = "Searches the web and summarizes the results."
    schema = SearchSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        query: str,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        prompt = f"Summarize the following web search query: {query}"
        return await ai_client.generate_response(
            chat_id=context.chat_id,
            prompt=prompt,
            history=[],
        )