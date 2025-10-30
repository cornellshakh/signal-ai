import uuid
import structlog
from functools import wraps
from ..core.command import BaseCommand


def command(name, help=""):
    def decorator(cls):
        original_instance = cls()

        class CommandWrapper(BaseCommand):
            @property
            def name(self) -> str:
                return name

            @property
            def description(self) -> str:
                return help

            async def handle(self, c, args):
                await original_instance.handle(c, args)

        return CommandWrapper

    return decorator


def subcommand(parent, name, help=""):
    def decorator(func):
        return func

    return decorator


def argument(name, type=str, help=""):
    def decorator(func):
        return func

    return decorator


def with_correlation_id(func):
    """
    A decorator that adds a correlation_id to the log context.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        correlation_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        try:
            return await func(*args, **kwargs)
        finally:
            structlog.contextvars.clear_contextvars()

    return wrapper
