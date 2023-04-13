from rich.console import Console

from esmerald.core.terminal.base import Base, OutputColour

console = Console()


class Terminal(Base):
    """Base output class for the terminal"""

    def write_success(
        self,
        message: str,
        colour: str = OutputColour.SUCCESS,
    ) -> None:
        """Outputs the successes to the console"""
        message = self.message(message, colour)
        return message

    def write_info(
        self,
        message: str,
        colour: str = OutputColour.INFO,
    ) -> None:
        """Outputs the info to the console"""
        message = self.message(message, colour)
        return message

    def write_warning(
        self,
        message: str,
        colour: str = OutputColour.WARNING,
    ) -> None:
        """Outputs the warnings to the console"""
        message = self.message(message, colour)
        return message

    def write_error(
        self,
        message: str,
        colour: str = OutputColour.ERROR,
    ) -> None:
        """Outputs the errors to the console"""
        message = self.message(message, colour)
        return message

    def write(self, message: str) -> None:
        console.print(message)

    def message(self, message: str, colour: str) -> str:
        """Returns a message formated with specific colours"""
        return f"[{colour}]{message}[/{colour}]"
