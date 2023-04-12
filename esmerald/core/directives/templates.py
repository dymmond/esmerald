import os
import shutil
import stat
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Union

import click
from jinja2 import Environment, FileSystemLoader

import esmerald
from esmerald.core.directives.base import BaseDirective


class TemplateDirective(BaseDirective):
    """
    Copy either an Esmerald application layout template or an Esmerald project
    layout.
    """

    url_schemes = ["http", "https", "ftp"]

    rewrite_template_suffixes = (
        (".py-tpl", ".py"),
        (".e-tpl", ""),
    )

    def add_arguments(self, parser: Any) -> Any:
        click.argument("name", type=str, help="Name of the application or project.")
