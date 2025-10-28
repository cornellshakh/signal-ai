import unittest

from src.signal_ai.core.tool_manager import ToolManager
from src.signal_ai.tools.web_search import WebSearchTool
from src.signal_ai import commands, tools


class TestToolManager(unittest.TestCase):
    def test_discover_tools(self):
        """
        Tests that the ToolManager can discover tools from multiple packages.
        """
        tool_manager = ToolManager(command_package=commands, tool_package=tools)

        # Check if a known command is discovered
        self.assertIn("ping", tool_manager.tools)

        # Check if a new tool is discovered
        self.assertIn("web_search", tool_manager.tools)
        self.assertIsInstance(tool_manager.tools["web_search"], WebSearchTool)

    def test_get_tool_schemas(self):
        """
        Tests that the schema generation works correctly for tools with Pydantic models.
        """
        tool_manager = ToolManager(command_package=commands, tool_package=tools)
        schemas = tool_manager.get_tool_schemas()

        # Find the web_search schema
        web_search_schema = next(
            (s for s in schemas if s.name == "web_search"), None
        )

        self.assertIsNotNone(web_search_schema)
        assert web_search_schema is not None
        self.assertEqual(web_search_schema.name, "web_search")
        self.assertIn("query", web_search_schema.parameters.properties)
        self.assertEqual(
            web_search_schema.parameters.properties["query"].type, "string"
        )
        self.assertIn("query", web_search_schema.parameters.required)

    def test_get_tool_schemas_no_schema(self):
        """
        Tests that tools without an ArgsSchema are not included in the schema list.
        """
        tool_manager = ToolManager(command_package=commands, tool_package=tools)
        schemas = tool_manager.get_tool_schemas()

        # Find the ping schema (which shouldn't exist)
        ping_schema = next((s for s in schemas if s.name == "ping"), None)

        self.assertIsNone(ping_schema)


if __name__ == "__main__":
    unittest.main()
