import shlex
import copy
import re
from typing import List, cast

from signalbot import Context, Message

from ...bot import SignalAIBot
from ...core.ai_client import AIClient
from ...core.decorators import command


@command("new", "Create a new conversation group.")
class NewConversationCommand:
    """
    A command to create a new conversation group with a prompt.
    """

    async def handle(self, c: Context, args: List[str]):
        """
        Handles the new conversation command.
        """
        if not args:
            await c.reply("Usage: !new <prompt>")
            return

        prompt = " ".join(args)
        bot = cast(SignalAIBot, c.bot)

        if not bot.ai_client or not bot.prompt_manager:
            await c.reply("AI client or prompt manager is not configured.")
            return

        try:
            # Generate a group name from the prompt
            try:
                group_name_prompt = bot.prompt_manager.get("generate_group_name", prompt=prompt)
            except ValueError:
                await c.reply("I can't generate a group name right now. The required prompt is missing from my configuration.")
                return
            group_name = await bot.ai_client.generate_response(
                chat_id=c.message.source, prompt=group_name_prompt, history=[]
            )
            # Sanitize the group name to remove markdown characters
            group_name = re.sub(r'[*_~`[\]()]', "", group_name.strip().strip('"'))

            # Create the group
            user_uuid = c.message.source_uuid
            if not user_uuid:
                await c.reply("Could not identify your user UUID to create the group.")
                return

            if not bot.group_manager:
                await c.reply("Group manager is not configured.")
                return

            group_info = await bot.group_manager.create(group_name, [user_uuid])
            group_id = group_info.get("id")
            if not group_id:
                await c.reply(
                    "Group created, but could not retrieve the group ID to send a confirmation."
                )
                return

            # Force the bot to update its internal list of groups
            await bot._detect_groups()

            # Set the group mode to "ai"
            if bot.persistence_manager:
                group_context = bot.persistence_manager.load_context(group_id)
                group_context.config.mode = "ai"
                bot.persistence_manager.save_context(group_id)

            # Generate an initial response from the AI and send it to the new group
            ai_response = await bot.ai_client.generate_response(
                chat_id=group_id, prompt=prompt, history=[]
            )
            await bot.send(group_id, ai_response, text_mode="styled")

            await c.reply(
                f"I've created the group '**{group_name}**' and added you to it.",
                text_mode="styled",
            )

        except Exception as e:
            await c.reply(f"An error occurred: {e}")
