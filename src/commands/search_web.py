import logging
import requests
import json
import os
from signalbot import Command, Context, triggered
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

class SearchWebCommand(Command):
    def describe(self) -> str:
        return "Search the web using Open-WebSearch."

    @triggered("!search")
    async def handle(self, c: Context) -> None:
        """Search the web and send the results."""
        log.info("!!!!!!!!!!!! SEARCH COMMAND HANDLE !!!!!!!!!!!!")
        log.info(f"Received message: {c.message.text}")
        query = c.message.text.split(' ', 1)[1] if len(c.message.text.split()) > 1 else None
        log.info(f"Parsed query: {query}")

        if not query:
            await c.send("Please provide a search query.")
            return

        try:
            url = os.environ.get("OPEN_WEBSEARCH_URL", "http://open-web-search:3000/mcp")
            log.info(f"OPEN_WEBSEARCH_URL: {url}")
            headers = {"Content-Type": "application/json"}
            data = {
                "server_name": "web-search",
                "tool_name": "search",
                "arguments": {
                    "query": query,
                    "limit": 3,
                    "engines": ["google"],
                },
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            results = response.json()

            if results:
                message = f"Search results for '{query}':\n"
                for result in results:
                    message += f"- {result['title']}: {result['url']}\n"
                await c.send(message)
            else:
                await c.send("No results found.")

        except requests.exceptions.RequestException as e:
            log.exception(f"Error searching the web: {e}")
            await c.send(f"Error searching the web: {e}")
        except Exception as e:
            await c.send(f"An unexpected error occurred: {e}")
