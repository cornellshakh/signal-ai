from typing import List, cast
from datetime import datetime, timedelta
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


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

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        scheduler = bot.scheduler
        if not scheduler:
            await c.reply("Scheduler not available.")
            return

        if len(args) < 3:
            await c.reply(
                "Usage: `!remind (in|at) <time> <message>`", text_mode="styled"
            )
            return

        when_type = args[0]
        time_str = args[1]
        message = " ".join(args[2:])

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
                scheduler.add_job(
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

                scheduler.add_job(
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
        else:
            await c.reply(f"Unknown subcommand: `{when_type}`.", text_mode="styled")
