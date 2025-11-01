import asyncio
import json
from typing import Dict, Set

import structlog

from signal_ai.domain.context import AppContext
from signal_ai.infrastructure.persistence import PersistenceManager

log = structlog.get_logger()


class StateManager:
    def __init__(self, persistence_manager: PersistenceManager):
        self._persistence_manager = persistence_manager
        self._contexts: Dict[str, AppContext] = {}
        self._self_sent_messages: Set[str] = set()

    def add_self_sent_message(self, message: str) -> None:
        """
        Adds a message to the cache of self-sent messages.
        """
        self._self_sent_messages.add(message)

    def is_self_sent_message(self, message: str) -> bool:
        """
        Checks if a message is in the cache of self-sent messages.
        """
        if message in self._self_sent_messages:
            self._self_sent_messages.remove(message)
            return True
        return False

    async def load_context(self, chat_id: str) -> AppContext:
        """
        Loads a chat context from the cache or database, or creates a new one.
        """
        if chat_id in self._contexts:
            return self._contexts[chat_id]

        log.info("state.load.start", chat_id=chat_id)
        context_json = await self._persistence_manager.get(f"context:{chat_id}")
        if context_json:
            log.info("state.load.cache.hit", chat_id=chat_id, data=context_json)
            context_data = json.loads(context_json)
            context_data["chat_id"] = chat_id
            context = await asyncio.to_thread(AppContext.model_validate, context_data)
        else:
            log.info("state.load.cache.miss", chat_id=chat_id)
            context = AppContext(chat_id=chat_id)
            await self.save_context(context)
        log.info("state.load.end", chat_id=chat_id)

        self._contexts[chat_id] = context
        return context

    async def save_context(self, context: AppContext) -> None:
        """
        Saves a chat context to the database and updates the cache.
        """
        log.info("state.save.start", chat_id=context.chat_id)
        data = context.model_dump(exclude_none=True)
        data["chat_id"] = context.chat_id
        await self._persistence_manager.set(
            f"context:{context.chat_id}", json.dumps(data)
        )
        self._contexts[context.chat_id] = context
        log.info("state.save.end", chat_id=context.chat_id)