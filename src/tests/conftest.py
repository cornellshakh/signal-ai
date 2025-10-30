import pytest
from unittest.mock import MagicMock
import signalbot

from signal_ai.core.context import AppContext, Context


@pytest.fixture
def app_context():
    """
    Provides a mock AppContext for testing.
    """
    # Mock the persistent context
    mock_persistent_context = MagicMock(spec=Context)
    mock_persistent_context.history = []

    # Mock the raw signalbot.Context
    mock_raw_context = MagicMock(spec=signalbot.Context)
    mock_raw_context.message = MagicMock()
    mock_raw_context.message.source = "test_chat_id"
    mock_raw_context.message.sender = "test_sender_id"
    mock_raw_context.message.text = "Hello, world!"
    mock_raw_context.bot = MagicMock()

    # Create the AppContext
    return AppContext(
        chat_id="test_chat_id",
        sender_id="test_sender_id",
        message_text="Hello, world!",
        persistent_context=mock_persistent_context,
        raw_context=mock_raw_context,
    )