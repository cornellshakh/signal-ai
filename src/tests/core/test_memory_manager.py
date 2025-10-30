import pytest
from unittest.mock import MagicMock, AsyncMock

from signal_ai.core.memory_manager import MemoryManager, ShortTermMemoryBackend
from signal_ai.core.context import Context
from signal_ai.core.persistence import PersistenceManager


class TestMemoryManager:
    def test_add_memory_calls_backend(self):
        """Test that add_memory calls the backend's add_memory."""
        mock_backend = MagicMock()
        memory_manager = MemoryManager(backend=mock_backend)
        chat_id = "test_chat"
        memory_text = "this is a test memory"
        memory_manager.add_memory(chat_id, memory_text)
        mock_backend.add_memory.assert_called_once_with(chat_id, memory_text)

    def test_retrieve_relevant_memories_calls_backend(self):
        """Test that retrieve_relevant_memories calls the backend's method."""
        mock_backend = MagicMock()
        memory_manager = MemoryManager(backend=mock_backend)
        chat_id = "test_chat"
        query_text = "test query"
        memory_manager.retrieve_relevant_memories(chat_id, query_text, k=3)
        mock_backend.retrieve_relevant_memories.assert_called_once_with(
            chat_id, query_text, 3
        )


@pytest.mark.asyncio
class TestShortTermMemoryBackend:
    @pytest.fixture
    def mock_persistence_manager(self):
        return AsyncMock(spec=PersistenceManager)

    @pytest.fixture
    def backend(self, mock_persistence_manager):
        return ShortTermMemoryBackend(persistence_manager=mock_persistence_manager)

    async def test_add_memory(self, backend, mock_persistence_manager):
        """Test that add_memory correctly appends to the chat history."""
        chat_id = "test_chat"
        memory_text = "new memory"

        # Mock the context object that the persistence manager would load
        mock_context = Context()
        mock_persistence_manager.load_context.return_value = mock_context

        await backend.add_memory(chat_id, memory_text)

        # Verify that the memory was added in the correct format
        assert len(mock_context.history) == 1
        assert mock_context.history[0] == {"role": "user", "parts": [memory_text]}

        # Verify that the context was saved
        mock_persistence_manager.save_context.assert_called_once_with(chat_id)

    async def test_retrieve_relevant_memories_keyword_search(
        self, backend, mock_persistence_manager
    ):
        """Test the keyword-based retrieval logic."""
        chat_id = "test_chat"
        query = "find relevant info"

        history = [
            {"role": "user", "parts": ["a completely unrelated message"]},
            {"role": "model", "parts": ["some model response"]},
            {"role": "user", "parts": ["this is very relevant"]},
            {"role": "user", "parts": ["another piece of relevant info"]},
        ]

        mock_context = Context()
        mock_context.history = history
        mock_persistence_manager.load_context.return_value = mock_context

        results = await backend.retrieve_relevant_memories(chat_id, query, k=5)

        assert len(results) == 2
        assert "this is very relevant" in results
        assert "another piece of relevant info" in results
        # Check that the most relevant (higher score) is first
        assert results[0] == "another piece of relevant info"
