import os
import subprocess
from datetime import datetime
from pathlib import Path

import redis.asyncio as redis
import structlog
from sqlalchemy import Column, String, Text, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


log = structlog.get_logger()


class KeyValueModel(Base):
    __tablename__ = "key_value"
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


class PersistenceManager:
    """Handles the underlying storage and caching mechanisms."""

    def __init__(self, db_url: str, redis_url: str, backup_dir: Path):
        self._engine = create_async_engine(db_url)
        self._async_session = async_sessionmaker(
            self._engine, expire_on_commit=False
        )
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._backup_dir = backup_dir
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        log.info("PersistenceManager initialized.")

    async def create_tables(self):
        """Creates the necessary database tables if they do not exist."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get(self, key: str) -> str | None:
        """Gets a value from the cache or database."""
        cached_value = await self._redis.get(key)
        if cached_value:
            return cached_value

        async with self._async_session() as session:
            stmt = select(KeyValueModel.value).where(KeyValueModel.key == key)
            result = await session.execute(stmt)
            scalar_result = result.scalar_one_or_none()
            if scalar_result:
                await self._redis.set(key, scalar_result)
                return scalar_result
            return None

    async def set(self, key: str, value: str) -> None:
        """Sets a value in the database and cache."""
        async with self._async_session() as session:
            async with session.begin():
                await session.merge(KeyValueModel(key=key, value=value))
        await self._redis.set(key, value)

    def backup_database(self):
        """
        Creates a timestamped backup of the PostgreSQL database using pg_dump.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"db_backup_{timestamp}.sql"

        db_url = self._engine.url
        command = [
            "pg_dump",
            "-h",
            db_url.host,
        ]
        if db_url.port:
            command.extend(["-p", str(db_url.port)])
        command.extend(
            [
                "-U",
                db_url.username,
                "-d",
                db_url.database,
                "-f",
                str(backup_path),
            ]
        )

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
            log.info("db.backup.success", backup_path=backup_path)
        except subprocess.CalledProcessError as e:
            log.error("db.backup.failed", error=e.stderr, exc_info=True)
        except FileNotFoundError:
            log.error("db.backup.pg_dump_not_found")