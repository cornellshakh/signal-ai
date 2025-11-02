import asyncio
import structlog

from signal_client.context import Context as SignalBotContext
from .context import to_app_context
from .tool_manager import ToolManager
from .reasoning_engine import ReasoningEngine
from .persistence import PersistenceManager
from .command import TextResult, ErrorResult, ImageResult
from .decorators import with_correlation_id

log = structlog.get_logger()


class MessageHandler:
    """
    The message handler, decoupled from the SignalBot library.
    """

    def __init__(
        self,
        tool_manager: ToolManager,
        reasoning_engine: ReasoningEngine,
        persistence_manager: PersistenceManager,
        max_workers: int = 4,
    ):
        self.tool_manager = tool_manager
        self.reasoning_engine = reasoning_engine
        self.persistence_manager = persistence_manager
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers = []

    async def start(self):
        """
        Starts the message handler workers.
        """
        self.workers = [
            asyncio.create_task(self._worker()) for _ in range(self.max_workers)
        ]

    async def handle(self, context: SignalBotContext):
        """
        Asynchronously handles an incoming message.
        """
        await self.queue.put(context)

    async def _worker(self):
        """
        The worker task that processes messages from the queue.
        """
        while True:
            context = await self.queue.get()
            try:
                await self._handle_message(context)
            finally:
                self.queue.task_done()

    @with_correlation_id
    async def _handle_message(self, context: SignalBotContext):
        """
        Internal message handling logic.
        """
        app_context = await to_app_context(context, self.persistence_manager)
        log.info("message.received", message=app_context.message_text)
        try:
            if app_context.message_text.startswith("!"):
                command_name = app_context.message_text.split()[0][1:]
                result = await self.tool_manager.dispatch(command_name, app_context)
                if isinstance(result, TextResult):
                    await context.reply(result.text, text_mode="styled")
                elif isinstance(result, ErrorResult):
                    await context.reply(result.error)
                elif isinstance(result, ImageResult):
                    await context.reply(
                        f"Image generated (placeholder): {result.image_path}"
                    )
            else:
                await self.reasoning_engine.handle_message(app_context)
        except Exception:
            log.exception("message.handle.failed")
            await context.reply("An unexpected error occurred.")