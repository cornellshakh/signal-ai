from typing import Any, Optional, Union, cast

from ...bot import SignalAIBot
from ...core.command import BaseCommand, TextResult, ErrorResult
from ...core.context import AppContext


class ImageCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "image"

    @property
    def description(self) -> str:
        return "Generates an image based on a prompt."

    def help(self) -> str:
        return "Usage: `!image [prompt]`\n\n" "Generates an image based on a prompt."

    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        bot = cast(SignalAIBot, c.raw_context.bot)
        if not bot.ai_client:
            return ErrorResult("AI client not available.")

        if not args:
            return ErrorResult("Usage: `!image [prompt]`")

        prompt = " ".join(args)
        # This is a placeholder. In a real implementation, you would generate an image
        # and return an ImageResult.
        response = await bot.ai_client.generate_response(
            chat_id=c.chat_id,
            prompt=f"Create an image based on the prompt: {prompt}",
            history=[],
        )
        return TextResult(response)