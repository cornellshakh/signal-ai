from typing import Any, Optional, Union, cast
from datetime import datetime, timedelta

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class RemindCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "remind"

    @property
    def description(self) -> str:
        return "Sets a reminder."

    def help(self) -> str:
        return (
            "Usage: `!remind (in|at) <time> <message>`\n\n"
            "Sets a reminder.\n\n"
            "**Subcommands:**\n"
            "- `in <time> <message>`: Set a reminder in a relative amount of time (e.g., `10s`, `5m`, `1h`).\n"
            "- `at <time> <message>`: Set a reminder at a specific time (e.g., `14:30`)."
        )

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        scheduler = bot.scheduler
        if not scheduler:
            return ErrorResult("Scheduler not available.")

        if not args or len(args) < 3:
            return ErrorResult("Usage: `!remind (in|at) <time> <message>`")

        when_type = args[0]
        time_str = args[1]
        message = " ".join(args[2:])

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
                scheduler.add_job(
                    c.raw_context.reply,
                    "date",
                    run_date=run_date,
                    args=[f"Reminder: {message}"],
                    kwargs={"text_mode": "styled"},
                )
                return TextResult(
                    f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."
                )

            except (ValueError, IndexError):
                return ErrorResult(
                    "Invalid time format for 'in'. Use something like `10s`, `5m`, or `1h`."
                )

        elif when_type == "at":
            try:
                run_date = datetime.strptime(time_str, "%H:%M")
                run_date = datetime.now().replace(
                    hour=run_date.hour, minute=run_date.minute, second=0, microsecond=0
                )
                if run_date < datetime.now():
                    run_date += timedelta(days=1)

                scheduler.add_job(
                    c.raw_context.reply,
                    "date",
                    run_date=run_date,
                    args=[f"Reminder: {message}"],
                    kwargs={"text_mode": "styled"},
                )
                return TextResult(
                    f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."
                )

            except ValueError:
                return ErrorResult("Invalid time format for 'at'. Use HH:MM.")
        else:
            return ErrorResult(f"Unknown subcommand: `{when_type}`.")