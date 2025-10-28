import aiohttp
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import SignalAIBot


class GroupManager:
    """
    Manages all group-related operations for the SignalAIBot, acting as a
    wrapper around the signal-cli-rest-api's group endpoints.
    """

    def __init__(self, bot: "SignalAIBot"):
        """
        Initializes the GroupManager with a reference to the main bot instance.
        """
        self._bot = bot

    async def create(
        self,
        name: str,
        members: List[str],
        description: Optional[str] = None,
        permissions: Optional[Dict[str, str]] = None,
        group_link: Optional[str] = None,
        expiration_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new group with a given name and list of members.
        """
        uri = self._bot._signal._signal_api_uris.groups_uri()
        payload = {"name": name, "members": members}
        if description:
            payload["description"] = description
        if permissions:
            payload["permissions"] = permissions
        if group_link:
            payload["group_link"] = group_link
        if expiration_time:
            payload["expiration_time"] = expiration_time

        async with aiohttp.ClientSession() as session:
            async with session.post(uri, json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all groups the bot is a member of.
        """
        return await self._bot._signal.get_groups()

    async def get(self, group_id: str) -> Dict[str, Any]:
        """
        Retrieves the details of a specific group.
        """
        uri = self._bot._signal._signal_api_uris.group_id_uri(group_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def update(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> None:
        """
        Updates the properties of an existing group.
        """
        await self._bot._signal.update_group(
            group_id=group_id,
            name=name,
            description=description,
            base64_avatar=avatar,
        )

    async def add_members(self, group_id: str, members: List[str]) -> None:
        """
        Adds members to a group.
        """
        uri = f"{self._bot._signal._signal_api_uris.group_id_uri(group_id)}/members"
        payload = {"members": members}
        async with aiohttp.ClientSession() as session:
            async with session.post(uri, json=payload) as resp:
                resp.raise_for_status()

    async def remove_members(self, group_id: str, members: List[str]) -> None:
        """
        Removes members from a group.
        """
        uri = f"{self._bot._signal._signal_api_uris.group_id_uri(group_id)}/members"
        payload = {"members": members}
        async with aiohttp.ClientSession() as session:
            async with session.delete(uri, json=payload) as resp:
                resp.raise_for_status()

    async def add_admins(self, group_id: str, admins: List[str]) -> None:
        """
        Promotes members to admins.
        """
        uri = f"{self._bot._signal._signal_api_uris.group_id_uri(group_id)}/admins"
        payload = {"admins": admins}
        async with aiohttp.ClientSession() as session:
            async with session.post(uri, json=payload) as resp:
                resp.raise_for_status()

    async def delete(self, group_id: str) -> None:
        """
        Deletes a group.
        """
        uri = self._bot._signal._signal_api_uris.group_id_uri(group_id)
        async with aiohttp.ClientSession() as session:
            async with session.delete(uri) as resp:
                resp.raise_for_status()
