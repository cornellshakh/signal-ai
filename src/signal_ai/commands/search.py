from signalbot import Context
from ..core.ai_client import AIClient


async def handle_search(c: Context, args: list[str], ai_client: AIClient):
    """
    Handles the !search command.
    """
    if not args:
        await c.reply("Usage: `!search [query]`")
        return

    query = " ".join(args)
    prompt = f"Summarize the following web search query: {query}"
    response = await ai_client.generate_response(prompt)
    await c.reply(response)
