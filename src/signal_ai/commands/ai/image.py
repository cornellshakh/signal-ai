from typing import Optional
from signalbot import Command, Context, regex_triggered
from ...core.ai_client import AIClient


class ImageCommand(Command):
    def __init__(self, ai_client: AIClient):
        self._ai_client = ai_client

    def describe(self) -> str:
        return "Generates an image based on a prompt."

    @regex_triggered(r"^!ai image (.+)")
    async def handle(self, c: Context, prompt: str) -> None:
        # This is a placeholder. In a real implementation, you would generate an image
        # and send it as an attachment.
        response = await self._ai_client.generate_response(
            chat_id=c.message.source,
            prompt=f"Create an image based on the prompt: {prompt}",
            history=[],
        )
        await c.reply(response, text_mode="styled")
