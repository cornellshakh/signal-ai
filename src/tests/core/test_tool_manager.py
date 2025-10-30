import pytest
from unittest.mock import AsyncMock

from signal_ai.core.tool_manager import ToolManager
from signal_ai.tools.web_search import WebSearchTool


def test_discover_tools():
    """
    Tests that the ToolManager can discover tools from multiple modules.
    """
    tool_manager = ToolManager(
        module_paths=[
            "signal_ai.commands.system.ping",
            "signal_ai.tools.web_search",
        ]
    )

    # Check if a known command is discovered
    assert "ping" in tool_manager.tools

    # Check if a new tool is discovered
    assert "web_search" in tool_manager.tools
    assert isinstance(tool_manager.tools["web_search"], WebSearchTool)


@pytest.mark.asyncio
async def test_dispatch_known_command(app_context, mocker):
    """
    Tests that the dispatch method correctly calls a known command.
    """
    tool_manager = ToolManager(module_paths=["signal_ai.commands.system.ping"])
    app_context.message_text = "!ping"

    # Mock the handle method of the ping command
    mock_ping_handle = AsyncMock()
    mocker.patch.object(tool_manager.tools["ping"], "handle", mock_ping_handle)

    await tool_manager.dispatch(app_context)

    mock_ping_handle.assert_called_once_with(app_context, None)


@pytest.mark.asyncio
async def test_dispatch_unknown_command(app_context):
    """
    Tests that the dispatch method replies with an error for an unknown command.
    """
    tool_manager = ToolManager(module_paths=[])
    app_context.message_text = "!unknown"

    await tool_manager.dispatch(app_context)

    app_context.raw_context.reply.assert_called_once_with("Unknown command: unknown")
