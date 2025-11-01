from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from signal_ai.domain.context import AppContext
from signal_ai.domain.tool import BaseTool
from signal_ai.infrastructure.ai import AIClient
from signal_ai.infrastructure.signal import SignalTransport
from signal_ai.services.scheduler import SchedulerService
from signal_ai.services.state import StateManager


class RemindSchema(BaseModel):
    when_type: str = Field(..., description="The type of reminder (in, at).")
    time_str: str = Field(..., description="The time of the reminder.")
    message: str = Field(..., description="The message to send.")


class RemindTool(BaseTool):
    """
    Sets a reminder.
    """

    name = "remind"
    description = "Sets a reminder."
    schema = RemindSchema

    async def execute(
        self,
        context: AppContext,
        state_manager: StateManager,
        ai_client: AIClient,
        signal_transport: SignalTransport,
        scheduler_service: SchedulerService,
        when_type: str,
        time_str: str,
        message: str,
        **kwargs: Any,
    ) -> str:
        """
        Run the tool.
        """
        if when_type == "in":
            try:
                value = int(time_str[:-1])
                unit = time_str[-1]
                if unit == "s":
                    delta = timedelta(seconds=value)
                elif unit == "m":
                    delta = timedelta(minutes=value)
                elif unit == "h":
                    delta = timedelta(hours=value)
                else:
                    raise ValueError("Invalid time unit")

                run_date = datetime.now() + delta
                # The scheduling logic will be handled by the SchedulerService.
                # This is a placeholder for now.
                return f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."

            except (ValueError, IndexError):
                return "Invalid time format for 'in'. Use something like `10s`, `5m`, or `1h`."

        elif when_type == "at":
            try:
                run_date = datetime.strptime(time_str, "%H:%M")
                run_date = datetime.now().replace(
                    hour=run_date.hour, minute=run_date.minute, second=0, microsecond=0
                )
                if run_date < datetime.now():
                    run_date += timedelta(days=1)

                # The scheduling logic will be handled by the SchedulerService.
                # This is a placeholder for now.
                return f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."

            except ValueError:
                return "Invalid time format for 'at'. Use HH:MM."
        else:
            return f"Unknown subcommand: `{when_type}`."