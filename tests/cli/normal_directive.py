from typing import Any

from ravyn.core.directives import BaseDirective
from ravyn.core.terminal import Print

printer = Print()


class Directive(BaseDirective):
    help: str = "Creates a superuser"

    async def handle(self, *args: Any, **options: Any) -> Any:
        """
        Generates a superuser
        """
        printer.write_success("Working")
