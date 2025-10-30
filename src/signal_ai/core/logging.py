import logging
import os
import sys
import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder


def configure_logging():
    """
    Configures logging for the application using structlog.
    """
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_renderer_str = os.environ.get("LOG_RENDERER", "console").lower()

    try:
        log_level = getattr(logging, log_level_str)
    except AttributeError:
        log_level = logging.INFO

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        CallsiteParameterAdder(
            [
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            ]
        ),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_renderer_str == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence noisy third-party loggers
    for logger_name in ["websockets", "apscheduler", "tzlocal"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
