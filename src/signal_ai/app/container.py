from dependency_injector import containers, providers
from pathlib import Path

from signal_ai.core.config import Settings
from signal_ai.core.config import Settings
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.persistence import PersistenceManager
from signal_ai.infrastructure.prompt import PromptManager
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.handler import MessageHandler
from signal_ai.services.reasoning import ReasoningEngine
from signal_ai.services.state import StateManager
from signal_ai.services.scheduler import SchedulerService
from signal_ai.services.tooling import ToolingService
from signal_ai.tools.ai.image import ImageTool
from signal_ai.tools.ai.search import SearchTool
from signal_ai.tools.config.config import ConfigTool
from signal_ai.tools.context.context import ContextTool
from signal_ai.tools.memory.remember import RememberTool
from signal_ai.tools.task.remind import RemindTool
from signal_ai.tools.task.todo import TodoTool
from signal_ai.tools.system.help import HelpTool
from signal_ai.tools.system.ping import PingTool


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    signal_transport = providers.Singleton(
        SignalTransport,
        config=config,
    )

    prompt_manager = providers.Singleton(
        PromptManager,
        "src/signal_ai/prompts.yaml",
    )

    ai_client = providers.Singleton(
        AIClient,
        api_key=config.provided.google_api_key,
        prompt_manager=prompt_manager,
    )

    persistence_manager = providers.Singleton(
        PersistenceManager,
        db_url=config.provided.database_url,
        redis_url=config.provided.redis_url,
        backup_dir=Path("/home/.local/share/signal-cli/backups"),
    )

    state_manager = providers.Singleton(
        StateManager,
        persistence_manager=persistence_manager,
    )

    scheduler_service = providers.Singleton(SchedulerService)

    tooling_service = providers.Singleton(ToolingService)

    tool_providers = providers.List(
        providers.Singleton(PingTool),
        providers.Singleton(HelpTool, tooling_service=tooling_service),
        providers.Singleton(RememberTool),
        providers.Singleton(ImageTool),
        providers.Singleton(SearchTool),
        providers.Singleton(ConfigTool),
        providers.Singleton(ContextTool),
        providers.Singleton(RemindTool),
        providers.Singleton(TodoTool),
    )

    reasoning_engine = providers.Singleton(
        ReasoningEngine,
        tooling_service=tooling_service,
        state_manager=state_manager,
        ai_client=ai_client,
        signal_transport=signal_transport,
    )

    message_handler = providers.Singleton(
        MessageHandler,
        reasoning_engine=reasoning_engine,
        state_manager=state_manager,
        signal_transport=signal_transport,
        config=config,
    )