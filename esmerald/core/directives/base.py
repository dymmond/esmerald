import argparse
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from pydantic import BaseConfig, BaseModel

import esmerald
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.directives.parsers import DirectiveParser
from esmerald.core.terminal.print import Print

printer = Print()


class BaseDirective(BaseModel, ABC):
    """The base class from which all directrives derive"""

    help: str = ""

    def get_version(self) -> str:
        """
        Returns the current version of Esmerald.
        """
        return esmerald.__version__

    def print_help(self, name: str, subdirective: str) -> str:
        """
        Prints the help of the directive.
        """
        parser = self.create_parser(name, subdirective)
        parser.print_help()

    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        """
        Entrypoint for directives and custom arguments
        """
        ...

    def add_base_argument(self, parser: Any, *args: Any, **kwargs: Dict[str, Any]):
        for arg in args:
            if arg in self.suppressed_base_arguments:
                kwargs["help"] = argparse.SUPPRESS
                break
        parser.add_argument(*args, **kwargs)

    def create_parser(self, name: str, subdirective: str, **kwargs):
        parser = DirectiveParser(
            prog="%s %s" % (os.path.basename(name), subdirective), description=self.help, **kwargs
        )
        self.add_arguments(parser)
        return parser

    def execute_from_command(self, argv: Any) -> None:
        """
        Executes dynamically the directive from the command line and passing the parameters
        """
        parser = self.create_parser(argv[0], argv[5])

        options = parser.parse_args(argv[6:])
        cmd_options = vars(options)

        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        try:
            self.run(*args, **cmd_options)
        except DirectiveError as e:
            printer.write_error("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)

    def run(self, *args: Any, **options: Any) -> Any:
        """
        Executes the handle()
        """
        output = self.handle(*args, **options)
        if output:
            printer.write_info(output)
        return output

    @abstractmethod
    def handle(self, *args: Any, **options: Any) -> Any:
        """The logic of the directive. Subclasses must implement this method"""
        raise NotImplementedError("subclasses of BaseDirective must provide a handle() method.")

    class Config(BaseConfig):
        extra = "allow"
        arbitrary_types_allowed = True
