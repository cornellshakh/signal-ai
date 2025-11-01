import asyncio
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from signal_ai.core.config import Settings
from signal_ai.domain.context import AppContext
from signal_ai.infrastructure.persistence import PersistenceManager


async def main():
    """
    Connects to the persistence layer, fetches the problematic context,
    and times the Pydantic validation.
    """
    print("Initializing settings...")
    settings = Settings()

    print("Initializing persistence manager...")
    persistence_manager = PersistenceManager(
        db_url=settings.database_url,
        redis_url=settings.redis_url,
        backup_dir=Path("backups"),
    )

    chat_id = "+420602880898"
    print(f"Fetching context for chat_id: {chat_id}")
    context_json = await persistence_manager.get(f"context:{chat_id}")

    if not context_json:
        print("No context found for this chat_id.")
        return

    print("Context fetched. Starting validation...")
    start_time = time.time()
    try:
        AppContext.model_validate_json(context_json)
        end_time = time.time()
        print(f"Validation successful. Time taken: {end_time - start_time:.4f} seconds")
    except Exception as e:
        end_time = time.time()
        print(f"Validation failed after {end_time - start_time:.4f} seconds.")
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())