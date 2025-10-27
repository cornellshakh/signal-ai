from datetime import datetime, timedelta
from signalbot import Context
from apscheduler.schedulers.background import BackgroundScheduler


async def handle_remind(c: Context, args: list[str], scheduler: BackgroundScheduler):
    """
    Handles the !remind command.
    """
    if len(args) < 3:
        await c.reply("Usage: `!remind [in|at] [time] [message]`")
        return

    when_type = args[0].lower()
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
                c.reply, "date", run_date=run_date, args=[f"Reminder: {message}"]
            )
            await c.reply(
                f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."
            )

        except (ValueError, IndexError):
            await c.reply(
                "Invalid time format for 'in'. Use something like `10s`, `5m`, or `1h`."
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
                c.reply, "date", run_date=run_date, args=[f"Reminder: {message}"]
            )
            await c.reply(
                f"Okay, I will remind you at {run_date.strftime('%H:%M:%S')}."
            )

        except ValueError:
            await c.reply("Invalid time format for 'at'. Use HH:MM.")
            return

    else:
        await c.reply("Usage: `!remind [in|at] [time] [message]`")
