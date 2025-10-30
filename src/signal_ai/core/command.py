from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Union

from .context import AppContext


class CommandResult(ABC):
    """Abstract base class for command results."""

    pass


class TextResult(CommandResult):
    """Represents a simple text result from a command."""

    def __init__(self, text: str):
        self.text = text


class ErrorResult(CommandResult):
    """Represents an error result from a command."""

    def __init__(self, error: str):
        self.error = error


class ImageResult(CommandResult):
    """Represents an image result from a command."""

    def __init__(self, image_path: str):
        self.image_path = image_path


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

    @property
    def ArgsSchema(self) -> Optional[Dict[str, Any]]:
        """The OpenAPI schema for the command's arguments."""
        return None

    @abstractmethod
    async def handle(
        self, c: AppContext, args: Optional[Any] = None
    ) -> Union[TextResult, ErrorResult, None]:
        """
        The main execution logic for the command.
        It now returns a result object instead of having side effects.
        """
        pass

    def help(self) -> str:
        """
        Returns a detailed help string for the command.
        Defaults to the description.
        """
        return self.description
