from typing import List, cast
from signalbot import Context
from ...bot import SignalAIBot
from ...core.command import BaseCommand


class ImageCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "image"

    @property
    def description(self) -> str:
        return "Generates an image based on a prompt."

    def help(self) -> str:
        return (
            "Usage: `!image [prompt]`\n\n"
            "Generates an image based on a prompt."
        )

    async def handle(self, c: Context, args: List[str]) -> None:
        bot = cast("SignalAIBot", c.bot)
        ai_client = bot.ai_client
        if not ai_client:
            await c.reply("AI client not available.")
            return

        if not args:
            await c.reply("Usage: `!image [prompt]`", text_mode="styled")
            return

        prompt = " ".join(args)
        # This is a placeholder. In a real implementation, you would generate an image
        # and send it as an attachment.
        response = await ai_client.generate_response(
            chat_id=c.message.source,
            prompt=f"Create an image based on the prompt: {prompt}",
            history=[],
        )
        await c.reply(response, text_mode="styled")
