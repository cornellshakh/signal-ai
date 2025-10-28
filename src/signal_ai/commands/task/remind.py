from typing import Optional
from datetime import datetime, timedelta
from signalbot import Command, Context, regex_triggered
from apscheduler.schedulers.background import BackgroundScheduler


class RemindCommand(Command):
    def __init__(self, scheduler: BackgroundScheduler):
        self._scheduler = scheduler

    def describe(self) -> str:
        return "Sets a reminder."

    def help(self) -> str:
        return (
            "Usage: `!task remind (in|at) <time> <message>`\n\n"
            "Sets a reminder.\n\n"
            "**Subcommands:**\n"
            "- `in <time> <message>`: Set a reminder in a relative amount of time (e.g., `10s`, `5m`, `1h`).\n"
            "- `at <time> <message>`: Set a reminder at a specific time (e.g., `14:30`)."
        )

    @regex_triggered(r"^!task remind (in|at) (.+?) (.+)")
    async def handle(
        self, c: Context, when_type: str, time_str: str, message: str
    ) -> None:
        if when_type == "in":
            try:
                # Simple parsing for "in" reminders, e.g., "10s", "5m", "1h"
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
                self._scheduler.add_job(
                    c.reply,
                    "date",
                    run_date=run_date,
                    args=[f"Reminder: {message}"],
                    kwargs={"text_mode": "styled"},
                )
                await c.reply(
                    f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}.",
                    text_mode="styled",
                )

            except (ValueError, IndexError):
                await c.reply(
                    "Invalid time format for 'in'. Use something like `10s`, `5m`, or `1h`.",
                    text_mode="styled",
                )
                return

        elif when_type == "at":
            try:
                run_date = datetime.strptime(time_str, "%H:%M")
                run_date = datetime.now().replace(
                    hour=run_date.hour, minute=run_date.minute, second=0, microsecond=0
                )
                if run_date < datetime.now():
                    run_date += timedelta(
                        days=1
                    )  # if time is in the past, schedule for tomorrow

                self._scheduler.add_job(
                    c.reply,
                    "date",
                    run_date=run_date,
                    args=[f"Reminder: {message}"],
                    kwargs={"text_mode": "styled"},
                )
                await c.reply(
                    f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}.",
                    text_mode="styled",
                )

            except ValueError:
                await c.reply(
                    "Invalid time format for 'at'. Use HH:MM.", text_mode="styled"
                )
                return
