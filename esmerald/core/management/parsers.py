from argparse import ArgumentParser
from typing import Any, Dict, Optional

from esmerald.core.management.exceptions import DirectiveError


class DirectiveParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent SystemExit.
    """

    def __init__(
        self,
        *,
        missing_args_message: Optional[str] = None,
        called_from_command_line: Optional[Any] = None,
        **kwargs: Dict[str, Any]
    ):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args: Any = None, namespace: str = None):
        if self.missing_args_message and not (
            args or any(not arg.startswith("-") for arg in args)
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise DirectiveError("Error: %s" % message)
