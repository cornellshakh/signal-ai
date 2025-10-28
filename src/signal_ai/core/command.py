from abc import ABC, abstractmethod
from typing import List

from signalbot import Context


class BaseCommand(ABC):
    """Abstract base class for all bot commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the command."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A short description of the command."""
        pass

    @abstractmethod
    async def handle(self, c: Context, args: List[str]) -> None:
        """The main execution logic for the command."""
        pass

    def help(self) -> str:
        """
        Returns a detailed help string for the command.
        Defaults to the description.
        """
        return self.description
