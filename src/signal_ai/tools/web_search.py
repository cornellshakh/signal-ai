import aiohttp
import structlog
from typing import Dict, Any

from ..core.command import BaseCommand
from signal_client.context import Context

log = structlog.get_logger()


class WebSearchTool(BaseCommand):
    """
    A tool to search the web for information.
    """

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Searches the web for the given query and returns the top results."

    @property
    def ArgsSchema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find information on the web.",
                }
            },
            "required": ["query"],
        }

    async def handle(self, c: Context, args: Dict[str, Any]) -> None:
        """
        Performs a web search using the DuckDuckGo API.
        """
        url = "https://api.duckduckgo.com/"
        params = {
            "q": args["query"],
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    results = data.get("RelatedTopics", [])
                    if not results:
                        await c.reply("No results found for your query.")
                        return

                    summary = ""
                    for i, result in enumerate(results[:3]):
                        summary += f"{i+1}. {result.get('Text')}\n"

                    await c.reply(summary)

        except aiohttp.ClientError as e:
            log.error("web_search.failed", error=str(e))
            await c.reply("Sorry, I couldn't perform the web search.")
