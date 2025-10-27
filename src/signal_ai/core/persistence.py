import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, cast

from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from .context import Context


class PersistenceManager:
    """Handles the loading, saving, and backup of chat contexts using TinyDB."""

    def __init__(self, db_path: Path):
        """
        Initializes the PersistenceManager.

        Args:
            db_path: The path to the TinyDB JSON file.
        """
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = TinyDB(self._db_path, storage=CachingMiddleware(JSONStorage))
        self._contexts: Dict[str, Context] = {}
        logging.info(f"PersistenceManager initialized with database at {self._db_path}")

    def load_context(self, chat_id: str) -> Context:
        """
        Loads a chat context from the database or creates a new one.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            The loaded or newly created Context object.
        """
        if chat_id in self._contexts:
            return self._contexts[chat_id]

        Chat = Query()
        result = self._db.get(Chat.id == chat_id)

        if result:
            logging.info(f"Loaded context for chat_id: {chat_id}")
            context = Context.model_validate(cast(dict, result).get("data"))
        else:
            logging.info(
                f"No existing context for chat_id: {chat_id}. Creating new one."
            )
            context = Context()

        self._contexts[chat_id] = context
        return context

    def save_context(self, chat_id: str):
        """
        Saves a chat context to the database.

        Args:
            chat_id: The unique identifier for the chat.
        """
        if chat_id not in self._contexts:
            logging.warning(
                f"Attempted to save a non-existent context for chat_id: {chat_id}"
            )
            return

        context = self._contexts[chat_id]
        Chat = Query()
        self._db.upsert(
            {"id": chat_id, "data": context.model_dump()}, Chat.id == chat_id
        )
        logging.info(f"Saved context for chat_id: {chat_id}")

    def backup_database(self):
        """
        Creates a timestamped backup of the database file.
        """
        backup_dir = self._db_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"db_{timestamp}.json"

        try:
            shutil.copy2(self._db_path, backup_path)
            logging.info(f"Database backup created at {backup_path}")
        except Exception as e:
            logging.error(f"Failed to create database backup: {e}")
