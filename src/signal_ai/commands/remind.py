import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from signalbot import Context

if TYPE_CHECKING:
    from ..bot import SignalAIBot


async def remind_command_handler(context: Context, args: list[str]):
    """
    Handles the 'remind' command.
    """
    if len(args) < 4 or args[0] != "me" or args[1] != "in":
        await context.send(
            "Usage: `@BotName remind me in <number> <minutes|hours> to <message>`",
            text_mode="styled",
        )
        return

    try:
        number = int(args[2])
        unit = args[3]
        if "to" not in args:
            raise ValueError("Missing 'to' in reminder message")

        message_index = args.index("to") + 1
        message = " ".join(args[message_index:])

        if unit.startswith("minute"):
            delta = timedelta(minutes=number)
        elif unit.startswith("hour"):
            delta = timedelta(hours=number)
        else:
            raise ValueError(f"Unknown time unit: {unit}")

        remind_time = datetime.now() + delta

        if TYPE_CHECKING:
            assert isinstance(context.bot, SignalAIBot)

        if context.bot.scheduler is None:
            await context.send(
                "⚠️ Error: Scheduler not initialized.", text_mode="styled"
            )
            return

        context.bot.scheduler.add_job(
            send_reminder,
            "date",
            run_date=remind_time,
            args=[context.bot, context.message.source, message],
        )

        await context.send(
            f"✅ **Got it.** I will remind you at `{remind_time.strftime('%I:%M %p')}` to \"{message}\".",
            text_mode="styled",
        )

    except (ValueError, IndexError) as e:
        logging.error(f"Error parsing reminder: {e}")
        await context.send(
            "Usage: `@BotName remind me in <number> <minutes|hours> to <message>`",
            text_mode="styled",
        )


async def send_reminder(bot: "SignalAIBot", chat_id: str, message: str):
    """
    Sends the reminder message.
    """
    await bot.send(chat_id, f"⏰ **Reminder:** {message}", text_mode="styled")
