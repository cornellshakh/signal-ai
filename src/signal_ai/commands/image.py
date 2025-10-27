from signalbot import Context
from ..core.ai_client import AIClient


async def handle_image(c: Context, args: list[str], ai_client: AIClient):
    """
    Handles the !image command.
    """
    if not args:
        await c.reply("Usage: `!image [prompt]`")
        return

    prompt = " ".join(args)
    # This is a placeholder. In a real implementation, you would generate an image
    # and send it as an attachment.
    response = await ai_client.generate_response(
        f"Create an image based on the prompt: {prompt}"
    )
    await c.reply(response)
