import argparse
from typing import Any, Type

from esmerald.core.directives import BaseDirective


class Directive(BaseDirective):
    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        # Add argments
        ...
