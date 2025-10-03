import argparse
from typing import Any, Type

from ravyn.core.directives import BaseDirective
from ravyn.core.terminal import Print

printer = Print()


class Directive(BaseDirective):
    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        """Arguments needed to create a user"""
        parser.add_argument("--first-name", dest="first_name", type=str, required=True)
        parser.add_argument("--last-name", dest="last_name", type=str, required=True)
        parser.add_argument("--username", dest="username", type=str, required=True)
        parser.add_argument("--email", dest="email", type=str, required=True)
        parser.add_argument("--password", dest="password", type=str, required=True)

    async def handle(self, *args: Any, **options: Any) -> Any:
        # Runs the handle logic in async mode
        ...
