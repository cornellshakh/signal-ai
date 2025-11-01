from typing import Dict

from signal_ai.domain.tool import BaseTool


import importlib
import inspect
import pkgutil
from typing import Dict

from signal_ai.domain.tool import BaseTool


from typing import Dict

from signal_ai.domain.tool import BaseTool


class ToolingService:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def wire(self, tools: list[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}