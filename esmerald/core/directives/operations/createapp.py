"""
Client to interact with Saffier models and migrations.
"""

from typing import Any

import click


@click.argument("name", type=str)
@click.command()
def create_app(directory: str) -> None:
    """Creates the scaffold of an application"""
