import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, Type

import structlog

from .command import BaseCommand
from .. import commands

log = structlog.get_logger()


class CommandDispatcher:
    """
    Automatically discovers, registers, and dispatches all commands
    that inherit from BaseCommand.
    """

    def __init__(self, command_package):
        self.commands: Dict[str, BaseCommand] = self._discover_commands(command_package)

    def _discover_commands(self, package) -> Dict[str, BaseCommand]:
        """
        Scans the given package for modules and classes that inherit from BaseCommand.
        """
        commands: Dict[str, BaseCommand] = {}
        package_path = Path(package.__file__).parent

        for path in package_path.glob("**/*.py"):
            if path.name == "__init__.py":
                continue

            relative_path = path.relative_to(package_path.parent)
            module_name_parts = relative_path.with_suffix("").parts
            module_name = ".".join(module_name_parts)
            
            try:
                module = importlib.import_module(f".{module_name}", package=package.__name__.rpartition('.')[0])
                for _, member in inspect.getmembers(module):
                    if (
                        inspect.isclass(member)
                        and issubclass(member, BaseCommand)
                        and member is not BaseCommand
                    ):
                        command_instance = member()
                        if command_instance.name in commands:
                            log.warning(
                                "command.discovery.duplicate",
                                name=command_instance.name,
                                module=module.__name__,
                            )
                            continue
                        commands[command_instance.name] = command_instance
                        log.info(
                            "command.discovery.registered",
                            name=command_instance.name,
                            module=module.__name__,
                        )
            except Exception as e:
                log.error(
                    "command.discovery.failed",
                    module_name=module_name,
                    error=str(e),
                    exc_info=True,
                )
        return commands

    async def dispatch(self, context, message_text: str):
        """
        Parses the message text and dispatches the command.
        """
        # Basic parsing logic for now. This will be improved.
        parts = message_text.strip().split()
        if not parts:
            return

        command_name = parts[0].lstrip("!")
        args = parts[1:]

        command = self.commands.get(command_name)
        if command:
            try:
                await command.handle(context, args)
            except Exception as e:
                log.error(
                    "command.dispatch.failed",
                    command=command_name,
                    error=str(e),
                    exc_info=True,
                )
                await context.reply(f"Error executing command: {command_name}")
        else:
            # In the future, this could suggest similar commands.
            await context.reply(f"Unknown command: {command_name}")
