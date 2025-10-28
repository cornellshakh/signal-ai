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
