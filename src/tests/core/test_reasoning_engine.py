import pytest
from unittest.mock import MagicMock, AsyncMock

from signal_ai.core.reasoning_engine import ReasoningEngine
from signal_ai.core.ai_client import AIClient
from signal_ai.core.tool_manager import ToolManager


@pytest.mark.asyncio
async def test_handle_message_does_not_crash(app_context):
    """
    Tests that the handle_message method can be called without crashing.
    This is a placeholder test, as the ReasoningEngine is not yet implemented.
    """
    mock_ai_client = MagicMock(spec=AIClient)
    mock_tool_manager = MagicMock(spec=ToolManager)

    reasoning_engine = ReasoningEngine(
        ai_client=mock_ai_client,
        tool_manager=mock_tool_manager,
    )

    # This will pass as long as the method doesn't raise an exception
    await reasoning_engine.handle_message(app_context)
