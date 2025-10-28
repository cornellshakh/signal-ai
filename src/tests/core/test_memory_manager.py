import unittest
from unittest.mock import MagicMock

from src.signal_ai.core.memory_manager import MemoryManager, ShortTermMemoryBackend
from src.signal_ai.core.context import Context
from src.signal_ai.core.persistence import PersistenceManager


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Set up a mock backend for the MemoryManager."""
        self.mock_backend = MagicMock()
        self.memory_manager = MemoryManager(backend=self.mock_backend)

    def test_add_memory_calls_backend(self):
        """Test that add_memory calls the backend's add_memory."""
        chat_id = "test_chat"
        memory_text = "this is a test memory"
        self.memory_manager.add_memory(chat_id, memory_text)
        self.mock_backend.add_memory.assert_called_once_with(chat_id, memory_text)

    def test_retrieve_relevant_memories_calls_backend(self):
        """Test that retrieve_relevant_memories calls the backend's method."""
        chat_id = "test_chat"
        query_text = "test query"
        self.memory_manager.retrieve_relevant_memories(chat_id, query_text, k=3)
        self.mock_backend.retrieve_relevant_memories.assert_called_once_with(
            chat_id, query_text, 3
        )


class TestShortTermMemoryBackend(unittest.TestCase):
    def setUp(self):
        """Set up a mock PersistenceManager."""
        self.mock_persistence_manager = MagicMock(spec=PersistenceManager)
        self.backend = ShortTermMemoryBackend(
            persistence_manager=self.mock_persistence_manager
        )

    def test_add_memory(self):
        """Test that add_memory correctly appends to the chat history."""
        chat_id = "test_chat"
        memory_text = "new memory"

        # Mock the context object that the persistence manager would load
        mock_context = Context()
        self.mock_persistence_manager.load_context.return_value = mock_context

        self.backend.add_memory(chat_id, memory_text)

        # Verify that the memory was added in the correct format
        self.assertEqual(len(mock_context.history), 1)
        self.assertEqual(
            mock_context.history[0], {"role": "user", "parts": [memory_text]}
        )

        # Verify that the context was saved
        self.mock_persistence_manager.save_context.assert_called_once_with(chat_id)

    def test_retrieve_relevant_memories_keyword_search(self):
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
        self.mock_persistence_manager.load_context.return_value = mock_context

        results = self.backend.retrieve_relevant_memories(chat_id, query, k=5)

        self.assertEqual(len(results), 2)
        self.assertIn("this is very relevant", results)
        self.assertIn("another piece of relevant info", results)
        # Check that the most relevant (higher score) is first
        self.assertEqual(results[0], "another piece of relevant info")


if __name__ == "__main__":
    unittest.main()
