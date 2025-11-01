import importlib
import inspect
import pkgutil
from typing import Dict, List, Any, Optional

import structlog

from .command import BaseCommand, CommandResult, TextResult, ErrorResult, ImageResult
from .context import AppContext

log = structlog.get_logger()


class ToolManager:
    """
    The tool manager, decoupled from the SignalBot library.
    """

    def __init__(self, module_paths: List[str]):
        self.tools: Dict[str, BaseCommand] = self._discover_tools(module_paths)

    def _discover_tools(self, module_paths: List[str]) -> Dict[str, BaseCommand]:
        tools = {}
        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)
                for _, member in inspect.getmembers(module):
                    if (
                        inspect.isclass(member)
                        and issubclass(member, BaseCommand)
                        and member is not BaseCommand
                    ):
                        tool_instance = member()
                        tools[tool_instance.name] = tool_instance
            except Exception as e:
                log.error(
                    "tool_discovery.error",
                    module=module_path,
                    error=str(e),
                    exc_info=True,
                )
        return tools

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns the OpenAPI schemas for all registered tools.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.ArgsSchema,
            }
            for tool in self.tools.values()
        ]

    async def dispatch(
        self,
        command_name: str,
        context: AppContext,
        **kwargs,
    ) -> Optional[CommandResult]:
        """
        Dispatches a command by name.
        """
        command = self.tools.get(command_name)

        if command:
            return await command.handle(context, kwargs)
        else:
            return ErrorResult(f"Unknown command: {command_name}")