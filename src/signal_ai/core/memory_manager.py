from abc import ABC, abstractmethod
from typing import List
from .persistence import PersistenceManager


class MemoryBackend(ABC):
    """Abstract base class for memory backends."""

    @abstractmethod
    def add_memory(self, chat_id: str, memory_text: str) -> None:
        pass

    @abstractmethod
    def retrieve_relevant_memories(
        self, chat_id: str, query_text: str, k: int = 5
    ) -> List[str]:
        pass


class MemoryManager:
    """Manages different memory backends."""

    def __init__(self, backend: MemoryBackend):
        self._backend = backend

    def add_memory(self, chat_id: str, memory_text: str) -> None:
        self._backend.add_memory(chat_id, memory_text)

    def retrieve_relevant_memories(
        self, chat_id: str, query_text: str, k: int = 5
    ) -> List[str]:
        return self._backend.retrieve_relevant_memories(chat_id, query_text, k)


class ShortTermMemoryBackend(MemoryBackend):
    """
    A memory backend that uses the PersistenceManager to store and retrieve
    recent conversation history.
    """

    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager

    def add_memory(self, chat_id: str, memory_text: str) -> None:
        """
        Adds a memory to the chat history.
        This backend formats the raw text into the dictionary structure the history expects.
        """
        chat_context = self._persistence_manager.load_context(chat_id)
        # For now, assume memories added this way are from the user.
        # This can be made more flexible later if needed.
        memory_object = {"role": "user", "parts": [memory_text]}
        chat_context.history.append(memory_object)
        self._persistence_manager.save_context(chat_id)

    def retrieve_relevant_memories(
        self, chat_id: str, query_text: str, k: int = 5
    ) -> List[str]:
        """
        Retrieves relevant memories using a simple keyword search.
        """
        chat_context = self._persistence_manager.load_context(chat_id)
        history = chat_context.history

        query_words = set(query_text.lower().split())

        # Score memories based on word overlap
        scored_memories = []
        for i, memory in enumerate(history):
            if memory.get("role") == "user":
                content = memory.get("parts", [""])[0]
                content_words = set(content.lower().split())
                score = len(query_words.intersection(content_words))
                if score > 0:
                    scored_memories.append((score, i, content))

        # Sort by score (descending) and then by original index (ascending)
        scored_memories.sort(key=lambda x: (x[0], -x[1]), reverse=True)
        return [content for score, i, content in scored_memories[:k]]
