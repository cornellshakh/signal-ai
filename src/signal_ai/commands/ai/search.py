from typing import List, cast
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class SearchCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Searches the web and summarizes the results."

    def help(self) -> str:
        return (
            "Usage: `!search [query]`\n\n"
            "Searches the web and summarizes the results."
        )

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        ai_client = bot.ai_client
        if not ai_client:
            await c.reply("AI client not available.")
            return

        if not args:
            await c.reply("Usage: `!search [query]`", text_mode="styled")
            return

        query = " ".join(args)
        prompt = f"Summarize the following web search query: {query}"
        response = await ai_client.generate_response(
            chat_id=c.message.source, prompt=prompt, history=[]
        )
        await c.reply(response, text_mode="styled")
