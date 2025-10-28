from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.ai_client import AIClient


class SearchCommand(Command):
    def __init__(self, ai_client: AIClient):
        self._ai_client = ai_client

    def describe(self) -> str:
        return "Searches the web and summarizes the results."

    @regex_triggered(r"^!ai search (.+)")
    async def handle(self, c: Context, query: str) -> None:
        prompt = f"Summarize the following web search query: {query}"
        response = await self._ai_client.generate_response(
            chat_id=c.message.source, prompt=prompt, history=[]
        )
        await c.reply(response, text_mode="styled")
