import asyncio
import signal

import structlog
from dependency_injector.wiring import inject, Provide

from signal_ai.app.container import Container
from signal_ai.infrastructure.persistence import PersistenceManager
from signal_ai.services.handler import MessageHandler
from signal_ai.services.tooling import ToolingService

log = structlog.get_logger()


@inject
async def main(
    message_handler: MessageHandler = Provide[Container.message_handler],
    tooling_service: ToolingService = Provide[Container.tooling_service],
    persistence_manager: PersistenceManager = Provide[Container.persistence_manager],
    tools: list = Provide[Container.tool_providers],
) -> None:
    tooling_service.wire(tools=tools)
    await persistence_manager.create_tables()
    log.info("Application starting up.")
    stop_event = asyncio.Event()

    def _signal_handler(*args):
        log.info("Shutdown signal received.")
        stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    log.info("Creating message handler task.")
    task = asyncio.create_task(message_handler.start())

    log.info("Waiting for shutdown signal.")
    await stop_event.wait()

    log.info("Shutting down.")
    await message_handler.stop()
    task.cancel()
    log.info("Shutdown complete.")


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])
    asyncio.run(main())