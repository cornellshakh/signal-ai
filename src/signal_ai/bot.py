from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from signalbot import SignalBot

from .core.ai_client import AIClient
from .core.message_handler import MessageHandler
from .core.persistence import PersistenceManager
from .core.prompt_manager import PromptManager
from .core.memory_manager import MemoryManager
from .core.tool_manager import ToolManager


class SignalAIBot(SignalBot):
    """
    The main application class for the Signal AI Bot.
    """

    def __init__(self, config):
        super().__init__(config)
        self.message_handler: Optional[MessageHandler] = None
        self.persistence_manager: Optional[PersistenceManager] = None
        self.prompt_manager: Optional[PromptManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.ai_client: Optional[AIClient] = None
        self.tool_manager: Optional[ToolManager] = None

    async def _async_post_init(self):
        """
        Perform async post-initialization setup.
        """
        await super()._async_post_init()
        if self.message_handler:
            await self.message_handler.start()


if __name__ == "__main__":
    import os
    from pathlib import Path
    from .core.config import settings
    from .core.reasoning_engine import ReasoningEngine
    from .core.memory_manager import ShortTermMemoryBackend
    from .commands.system.catch_all import CatchAllCommand
    from .core.logging import configure_logging

    configure_logging()

    # 1. Create bot instance
    config = {
        "signal_service": settings.signal_service,
        "phone_number": settings.signal_phone_number,
        "storage": {
            "type": "sqlite",
            "sqlite_db": "/home/.local/share/signal-cli/signalbot.sqlite",
        },
    }
    bot = SignalAIBot(config)

    # 2. Initialize and wire components
    backup_dir = Path("/home/.local/share/signal-cli/backups")
    backup_dir.mkdir(exist_ok=True)
    bot.persistence_manager = PersistenceManager(
        db_url=settings.database_url,
        redis_url=settings.redis_url,
        backup_dir=backup_dir,
    )
    bot.prompt_manager = PromptManager("src/signal_ai/prompts.yaml")
    bot.memory_manager = MemoryManager(
        ShortTermMemoryBackend(bot.persistence_manager)
    )
    bot.tool_manager = ToolManager(["src.signal_ai.commands"])
    bot.ai_client = AIClient(
        api_key=settings.google_api_key,
        prompt_manager=bot.prompt_manager,
        memory_manager=bot.memory_manager,
    )
    reasoning_engine = ReasoningEngine(
        ai_client=bot.ai_client,
        tool_manager=bot.tool_manager,
        persistence_manager=bot.persistence_manager,
        prompt_manager=bot.prompt_manager,
    )
    bot.message_handler = MessageHandler(
        tool_manager=bot.tool_manager,
        reasoning_engine=reasoning_engine,
        persistence_manager=bot.persistence_manager,
    )

    # 3. Register commands and start bot
    bot.register(CatchAllCommand())
    bot.start()