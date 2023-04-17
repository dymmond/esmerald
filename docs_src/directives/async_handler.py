import argparse
from typing import Any, Type

from esmerald.core.directives import BaseDirective
from esmerald.core.terminal import Print

printer = Print()


class Directive(BaseDirective):
    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        # Add argments
        ...

    async def handle(self, *args: Any, **options: Any) -> Any:
        # Runs the handle logic in async mode
        printer.write_success("Async mode handle run with success!")
