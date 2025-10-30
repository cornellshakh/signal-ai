from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


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

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.ai_client:
            return ErrorResult("AI client not available.")

        if not args:
            return ErrorResult("Usage: `!search [query]`")

        query = " ".join(args)
        prompt = f"Summarize the following web search query: {query}"
        response = await bot.ai_client.generate_response(
            chat_id=c.chat_id, prompt=prompt, history=[]
        )
        return TextResult(response)