"""
Client to interact with Saffier models and migrations.
"""

from typing import Any

import click

from esmerald.core.terminal import Print

printer = Print()


@click.argument("name", type=str)
@click.command()
def create_project(name: str) -> None:
    """
    Creates the scaffold of a project.

    How to run: `esmerald-admin createproject <NAME>`

    Example: `esmerald-admin createproject myproject`

    """

    printer.write_success(name)
