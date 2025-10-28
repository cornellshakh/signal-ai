import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Union

import structlog
from google.generativeai.types import FunctionDeclaration

from .command import BaseCommand

log = structlog.get_logger()


class ToolManager:
    """
    Automatically discovers, registers, and manages all tools
    that inherit from BaseCommand.
    """

    def __init__(self, command_package, tool_package):
        self.tools: Dict[str, BaseCommand] = self._discover_tools(
            [command_package, tool_package]
        )

    def get_tool_schemas(self) -> List[FunctionDeclaration]:
        """
        Generates a list of tool schemas for the AI model.
        """
        schemas = []
        for tool in self.tools.values():
            if tool.ArgsSchema:
                schema = FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.ArgsSchema,
                )
                schemas.append(schema)
        return schemas

    def _discover_tools(self, packages) -> Dict[str, BaseCommand]:
        """
        Scans the given packages for modules and classes that inherit from BaseCommand.
        """
        tools: Dict[str, BaseCommand] = {}
        for package in packages:
            package_path = Path(package.__file__).parent

            for path in package_path.glob("**/*.py"):
                if path.name == "__init__.py":
                    continue

                relative_path = path.relative_to(package_path.parent)
                module_name_parts = relative_path.with_suffix("").parts
                module_name = ".".join(module_name_parts)

                try:
                    module = importlib.import_module(
                        f".{module_name}", package=package.__name__.rpartition(".")[0]
                    )
                    for _, member in inspect.getmembers(module):
                        if (
                            inspect.isclass(member)
                            and issubclass(member, BaseCommand)
                            and member is not BaseCommand
                        ):
                            command_instance = member()
                            if command_instance.name in tools:
                                log.warning(
                                    "tool.discovery.duplicate",
                                    name=command_instance.name,
                                    module=module.__name__,
                                )
                                continue
                            tools[command_instance.name] = command_instance
                            log.info(
                                "tool.discovery.registered",
                                name=command_instance.name,
                                module=module.__name__,
                            )
                except Exception as e:
                    log.error(
                        "tool.discovery.failed",
                        module_name=module_name,
                        error=str(e),
                        exc_info=True,
                    )
        return tools

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

        command = self.tools.get(command_name)

        if command:
            try:
                final_args: Union[Dict[str, Any], str]
                if command.ArgsSchema:
                    args_dict: Dict[str, Any] = {}
                    schema_properties = command.ArgsSchema.get("properties", {})
                    arg_names = list(schema_properties.keys())
                    for i, arg_name in enumerate(arg_names):
                        if i < len(args):
                            args_dict[arg_name] = args[i]
                    final_args = args_dict
                else:
                    final_args = " ".join(args)
                await command.handle(context, final_args)
            except Exception as e:
                log.error(
                    "tool.dispatch.failed",
                    command=command_name,
                    error=str(e),
                    exc_info=True,
                )
                await context.reply(f"Error executing command: {command_name}")
        else:
            # In the future, this could suggest similar commands.
            await context.reply(f"Unknown command: {command_name}")
