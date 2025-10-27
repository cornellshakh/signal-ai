import asyncio
import json
import logging

from dotenv import load_dotenv
from signalbot import Command, Context, regex_triggered

load_dotenv()

log = logging.getLogger(__name__)


class SearchWebCommand(Command):
    def describe(self) -> str:
        return "Search the web using Open-WebSearch."

    @regex_triggered(r"^!search( .*)?$")
    async def handle(self, c: Context) -> None:
        """Search the web and send the results."""
        log.info("!!!!!!!!!!!! SEARCH COMMAND HANDLE !!!!!!!!!!!!")
        log.info(f"Received message: {c.message.text}")

        # Adjust query parsing for regex
        parts = c.message.text.split(" ", 1)
        query = parts[1].strip() if len(parts) > 1 else None
        log.info(f"Parsed query: {query}")

        if not query:
            await c.send("Please provide a search query.")
            return

        try:
            log.info("Attempting to use Open-WebSearch via stdio")

            cmd = "DEFAULT_SEARCH_ENGINE=duckduckgo open-websearch"

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={"MODE": "stdio"},
            )

            await asyncio.sleep(3)  # Give the server a moment to initialize

            request = {
                "jsonrpc": "2.0",
                "method": "search",
                "params": {"query": query, "limit": 3, "engines": ["duckduckgo"]},
                "id": 1,
            }

            if proc.stdin:
                log.info(f"Sending request: {json.dumps(request)}")
                proc.stdin.write(json.dumps(request).encode() + b"\n")
                await proc.stdin.drain()
            else:
                raise Exception("Failed to get stdin for subprocess")

            # Read stdout and stderr
            response_data, stderr_data = await proc.communicate()

            log.info(f"Process exited with code: {proc.returncode}")
            log.info(f"Received response: {response_data.decode()}")
            if stderr_data:
                log.error(f"Received stderr: {stderr_data.decode()}")

            if response_data:
                # Find the JSON part of the response
                json_response_str = None
                for line in response_data.decode().splitlines():
                    if line.strip().startswith("{"):
                        json_response_str = line
                        break

                if json_response_str:
                    response = json.loads(json_response_str)
                    if "result" in response:
                        results = response["result"]
                        if results:
                            message = f"Search results for '{query}':\n"
                            for result in results:
                                message += f"- {result['title']}: {result['url']}\n"
                            await c.send(message)
                        else:
                            await c.send("No results found.")
                    elif "error" in response:
                        error_message = response.get("error", {}).get(
                            "message", "Unknown error"
                        )
                        await c.send(f"Error from search tool: {error_message}")
                    else:
                        await c.send("Unknown response from search tool.")
                else:
                    await c.send("No valid JSON response from search tool.")
            else:
                await c.send("No response from search tool.")
                if stderr_data:
                    await c.send(f"Error details: {stderr_data.decode()}")

        except Exception as e:
            log.exception(f"An unexpected error occurred: {e}")
            await c.send(f"An unexpected error occurred: {e}")
