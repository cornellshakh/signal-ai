from typing import cast

from signalbot.command import Command

from ...bot import SignalAIBot
from signalbot.context import Context as SignalBotContext


class CatchAllCommand(Command):
    async def handle(self, context: SignalBotContext):
        bot = cast(SignalAIBot, context.bot)
        if bot.message_handler:
            await bot.message_handler.handle(context)