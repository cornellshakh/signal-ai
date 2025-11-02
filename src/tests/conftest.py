import pytest
from unittest.mock import MagicMock, AsyncMock
from signal_ai.core.context import AppContext, Context as PersistentContext, SignalBotContext

@pytest.fixture
def app_context():
    """
    Provides a mock-filled AppContext for testing.
    """
    # Create a mock for the persistent context
    mock_persistent_context = MagicMock(spec=PersistentContext)

    # Create a mock for the raw signal_client context
    mock_raw_context = MagicMock(spec=SignalBotContext)
    mock_raw_context.reply = AsyncMock()

    # Create the AppContext instance with mocks
    context = AppContext(
        chat_id="test_chat",
        sender_id="test_sender",
        message_text="",
        persistent_context=mock_persistent_context,
        raw_context=mock_raw_context,
    )
    return context