import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from .context import Context


class PersistenceManager:
    """
    Manages the persistence of chat contexts using TinyDB.
    """

    def __init__(self, db_path: Path):
        """
        Initializes the PersistenceManager.
        Args:
            db_path: The path to the TinyDB database file.
        """
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        storage = CachingMiddleware(JSONStorage)
        self._db = TinyDB(self._db_path, storage=storage)

    def load_context(self, chat_id: str) -> Context:
        """
        Loads the context for a given chat ID.
        If no context exists, a new one is created.
        Args:
            chat_id: The ID of the chat.
        Returns:
            The context for the chat.
        """
        ContextQuery = Query()
        result = self._db.search(ContextQuery.chat_id == chat_id)
        if result:
            logging.info(f"Loaded context for chat_id: {chat_id}")
            # result is a list, take the first element
            return Context.model_validate(result[0])
        else:
            logging.info(f"No context found for chat_id: {chat_id}, creating new one.")
            return Context(chat_id=chat_id)

    def save_context(self, context: Context) -> None:
        """
        Saves the context for a given chat.
        Args:
            context: The context to save.
        """
        ContextQuery = Query()
        self._db.upsert(
            context.model_dump(),
            ContextQuery.chat_id == context.chat_id,
        )
        logging.info(f"Saved context for chat_id: {context.chat_id}")

    def backup_database(self) -> None:
        """
        Creates a timestamped backup of the database file.
        """
        backup_path = self._db_path.parent / f"{self._db_path.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        try:
            shutil.copy(self._db_path, backup_path)
            logging.info(f"Database backed up to {backup_path}")
        except FileNotFoundError:
            logging.warning("Database file not found, skipping backup.")
        except Exception as e:
            logging.error(f"Error creating database backup: {e}")
