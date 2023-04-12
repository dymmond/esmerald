"""
Base classes for writing management directives (named directives which can
be rund through `esmerald-admin`).
"""
from typing import Any

from pydantic import BaseConfig, BaseModel
from rich.console import Console

import esmerald
from esmerald.core.terminal import Output

console = Console()


class Core(BaseModel, Output):
    class Config(BaseConfig):
        extra = "allow"
        arbitrary_types_allowed = True


class BaseDirective(Core):
    """The base class from which all directrives derive"""

    help: str = ""

    def get_version(self) -> str:
        """
        Returns the current version of Esmerald.
        """
        return esmerald.__version__

    def add_arguments(self, parser: Any) -> Any:
        """
        Entrypoint for directives and custom arguments
        """

    def handle(self, *args: Any, **options: Any) -> Any:
        """The logic of the directive. Subclasses must implement this method"""
        raise NotImplementedError("subclasses of BaseDirective must provide a handle() method.")
