import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import redis
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

from .context import Context


Base = declarative_base()


class ContextModel(Base):
    __tablename__ = "contexts"
    id = Column(String, primary_key=True)
    data = Column(Text, nullable=False)


class PersistenceManager:
    """Handles loading and saving of chat contexts using a hybrid Redis and PostgreSQL backend."""

    def __init__(self, db_url: str, redis_url: str, backup_dir: Path):
        """
        Initializes the PersistenceManager.

        Args:
            db_url: The connection URL for the PostgreSQL database.
            redis_url: The connection URL for the Redis server.
            backup_dir: The directory to store database backups.
        """
        self._engine = create_engine(db_url)
        self._Session = sessionmaker(bind=self._engine)
        self._redis = redis.from_url(redis_url)
        self._backup_dir = backup_dir
        self._contexts: Dict[str, Context] = {}
        self._create_tables()
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        logging.info("PersistenceManager initialized with PostgreSQL and Redis backends.")

    def _create_tables(self):
        """Creates the necessary database tables if they do not exist."""
        Base.metadata.create_all(self._engine)

    async def load_context(self, chat_id: str) -> Context:
        """
        Loads a chat context from the cache or database, or creates a new one.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            The loaded or newly created Context object.
        """
        if chat_id in self._contexts:
            return self._contexts[chat_id]

        # 1. Try to load from Redis cache
        cached_context = await self._redis.get(f"context:{chat_id}")
        if cached_context:
            logging.info(f"Loaded context for chat_id {chat_id} from cache.")
            context = Context.model_validate_json(cached_context.decode("utf-8"))
            self._contexts[chat_id] = context
            return context

        # 2. If cache miss, load from PostgreSQL
        session = self._Session()
        try:
            result = session.query(ContextModel).filter_by(id=chat_id).first()
            if result:
                logging.info(f"Loaded context for chat_id {chat_id} from database.")
                context = Context.model_validate_json(str(result.data))
                await self._redis.set(f"context:{chat_id}", context.model_dump_json())
            else:
                logging.info(f"No existing context for chat_id {chat_id}. Creating new one.")
                context = Context()
                await self.save_context(chat_id, context)  # Save immediately to ensure it exists in DB

            self._contexts[chat_id] = context
            return context
        finally:
            session.close()

    async def save_context(self, chat_id: str, context: Optional[Context] = None):
        """
        Saves a chat context to the database and updates the cache.

        Args:
            chat_id: The unique identifier for the chat.
            context: The context object to save. If None, the cached context is used.
        """
        context_to_save = context or self._contexts.get(chat_id)
        if not context_to_save:
            logging.warning(f"Attempted to save a non-existent context for chat_id: {chat_id}")
            return

        # 1. Save to PostgreSQL
        session = self._Session()
        try:
            context_json = context_to_save.model_dump_json()
            db_context = ContextModel(id=chat_id, data=context_json)
            session.merge(db_context)
            session.commit()
            logging.info(f"Saved context for chat_id {chat_id} to database.")
        except Exception as e:
            logging.error(f"Failed to save context for chat_id {chat_id} to database: {e}")
            session.rollback()
        finally:
            session.close()

        # 2. Update Redis cache
        await self._redis.set(f"context:{chat_id}", context_to_save.model_dump_json())
        logging.info(f"Updated cache for chat_id: {chat_id}")

    def backup_database(self):
        """
        Creates a timestamped backup of the PostgreSQL database using pg_dump.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"db_backup_{timestamp}.sql"
        
        db_url = self._engine.url
        command = [
            "pg_dump",
            "-h", db_url.host,
            "-p", str(db_url.port),
            "-U", db_url.username,
            "-d", db_url.database,
            "-f", str(backup_path),
        ]
        
        env = {}
        if db_url.password:
            env["PGPASSWORD"] = db_url.password

        try:
            subprocess.run(
                command,
                check=True,
                env={**os.environ, **env},
                capture_output=True,
                text=True,
            )
            logging.info(f"Database backup created successfully at {backup_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create database backup: {e.stderr}")
        except FileNotFoundError:
            logging.error("pg_dump command not found. Please ensure PostgreSQL client tools are installed.")
