import unittest
from unittest.mock import MagicMock, AsyncMock, PropertyMock

from google.generativeai.protos import FunctionCall, Part, Content, Candidate
from google.generativeai.types import AsyncGenerateContentResponse
from google.generativeai.types.content_types import ContentDict

from src.signal_ai.core.reasoning_engine import ReasoningEngine
from src.signal_ai.core.ai_client import AIClient
from src.signal_ai.core.tool_manager import ToolManager
from src.signal_ai.tools.meeting_scheduler import (
    CheckAvailabilityTool,
    ProposeMeetingTool,
    ConfirmMeetingTool,
)
from signalbot import Context


class TestReasoningEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up mock AIClient and ToolManager."""
        self.mock_ai_client = MagicMock(spec=AIClient)
        self.mock_tool_manager = MagicMock(spec=ToolManager)

        # Set up mock tools
        self.mock_check_availability = MagicMock(spec=CheckAvailabilityTool)
        self.mock_propose_meeting = MagicMock(spec=ProposeMeetingTool)
        self.mock_confirm_meeting = MagicMock(spec=ConfirmMeetingTool)

        self.mock_tool_manager.tools = {
            "check_availability": self.mock_check_availability,
            "propose_meeting": self.mock_propose_meeting,
            "confirm_meeting": self.mock_confirm_meeting,
        }

        self.reasoning_engine = ReasoningEngine(
            ai_client=self.mock_ai_client,
            tool_manager=self.mock_tool_manager,
        )

        # Mock context
        self.mock_context = MagicMock(spec=Context)
        self.mock_context.message = MagicMock()
        self.mock_context.message.source = "test_chat_id"
        self.mock_context.bot = MagicMock()

    def _create_mock_response(self, tool_name: str, tool_args: dict, is_final: bool = False) -> MagicMock:
        """Helper to create a mock AsyncGenerateContentResponse."""
        mock_response = MagicMock(spec=AsyncGenerateContentResponse)
        mock_candidate = MagicMock(spec=Candidate)

        if is_final:
            mock_response.text = "The meeting has been scheduled."
            mock_candidate.content = Content(parts=[])
        else:
            mock_function_call = FunctionCall(name=tool_name, args=tool_args)
            mock_part = Part(function_call=mock_function_call)
            mock_candidate.content = Content(parts=[mock_part])

        mock_response.candidates = [mock_candidate]
        return mock_response

    async def test_multi_step_meeting_scheduling(self):
        """Test a multi-step conversation to schedule a meeting."""

        # 1. Initial prompt
        prompt = "Schedule a meeting with Jane Doe for tomorrow."
        history = []

        # 2. AI responses mocked as GenerationResponse objects
        self.mock_ai_client.generate_response_with_tools = AsyncMock()
        self.mock_ai_client.generate_response_with_tools.side_effect = [
            self._create_mock_response("check_availability", {"dates": ["2023-10-28"]}),
            self._create_mock_response("propose_meeting", {"time": "2023-10-28T14:30:00", "attendees": ["jane.doe@example.com"]}),
            self._create_mock_response("confirm_meeting", {"meeting_id": "meeting-123"}),
            self._create_mock_response("", {}, is_final=True),
        ]

        # 3. Tool execution mocks
        self.mock_check_availability.handle = AsyncMock()
        self.mock_propose_meeting.handle = AsyncMock()
        self.mock_confirm_meeting.handle = AsyncMock()
        
        # Mock the ArgsSchema for each tool
        type(self.mock_check_availability).ArgsSchema = PropertyMock(return_value=MagicMock())
        type(self.mock_propose_meeting).ArgsSchema = PropertyMock(return_value=MagicMock())
        type(self.mock_confirm_meeting).ArgsSchema = PropertyMock(return_value=MagicMock())

        # 5. Execute the reasoning engine
        final_response = await self.reasoning_engine.execute(
            c=self.mock_context,
            prompt=prompt,
            history=history,
        )

        # 6. Assertions
        self.assertEqual(final_response, "The meeting has been scheduled.")
        self.assertEqual(self.mock_ai_client.generate_response_with_tools.call_count, 4)
        self.mock_check_availability.handle.assert_called_once()
        self.mock_propose_meeting.handle.assert_called_once()
        self.mock_confirm_meeting.handle.assert_called_once()


if __name__ == "__main__":
    unittest.main()
