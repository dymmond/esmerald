from abc import ABC, abstractmethod
from enum import Enum

from rich.console import Console

console = Console()


class OutputColour(str, Enum):
    SUCCESS = "green"
    INFO = "cyan"
    WARNING = "yellow"
    ERROR = "red"

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return str(self)


class Base(ABC):
    """Base output class for the terminal"""

    @abstractmethod
    def write_success(
        self, message: str, colour: str = OutputColour.SUCCESS, display: bool = False
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def write_info(
        self, message: str, colour: str = OutputColour.INFO, display: bool = False
    ) -> None:
        """Outputs the info to the console"""
        raise NotImplementedError()

    @abstractmethod
    def write_warning(
        self, message: str, colour: str = OutputColour.WARNING, display: bool = False
    ) -> None:
        """Outputs the warnings to the console"""

    @abstractmethod
    def write_error(
        self, message: str, colour: str = OutputColour.ERROR, display: bool = False
    ) -> None:
        """Outputs the errors to the console"""

    def message(self, message: str, colour: str) -> str:
        """Returns a message formated with specific colours"""
        return f"[{colour}]{message}[/{colour}]"


class Console(Base):
    """Base output class for the terminal"""

    def write_success(
        self, message: str, colour: str = OutputColour.SUCCESS, display: bool = False
    ) -> None:
        """Outputs the successes to the console"""
        message = self.message(message, colour)
        console.print(message)

    def write_info(
        self, message: str, colour: str = OutputColour.INFO, display: bool = False
    ) -> None:
        """Outputs the info to the console"""
        message = self.message(message, colour)
        console.print(message)

    def write_warning(
        self, message: str, colour: str = OutputColour.WARNING, display: bool = False
    ) -> None:
        """Outputs the warnings to the console"""
        message = self.message(message, colour)
        console.print(message)

    def write_error(
        self, message: str, colour: str = OutputColour.ERROR, display: bool = False
    ) -> None:
        """Outputs the errors to the console"""
        message = self.message(message, colour)
        console.print(message)


class ReturnWrapper(Base):
    """Base output class for the terminal"""

    def write_success(
        self, message: str, colour: str = OutputColour.SUCCESS, display: bool = False
    ) -> None:
        """Outputs the successes to the console"""
        message = self.message(message, colour)
        return message

    def write_info(
        self, message: str, colour: str = OutputColour.INFO, display: bool = False
    ) -> None:
        """Outputs the info to the console"""
        message = self.message(message, colour)
        return message

    def write_warning(
        self, message: str, colour: str = OutputColour.WARNING, display: bool = False
    ) -> None:
        """Outputs the warnings to the console"""
        message = self.message(message, colour)
        return message

    def write_error(
        self, message: str, colour: str = OutputColour.ERROR, display: bool = False
    ) -> None:
        """Outputs the errors to the console"""
        message = self.message(message, colour)
        return message

    def write(self, message: str) -> None:
        console.print(message)

    def message(self, message: str, colour: str) -> str:
        """Returns a message formated with specific colours"""
        return f"[{colour}]{message}[/{colour}]"
