"""
Client to interact with Saffier models and migrations.
"""

from typing import Any

import click


@click.option(
    "-d",
    "--directory",
    default=None,
    help=("Directory to place the app scaffold"),
)
@click.command()
@click.pass_context
def create_app(ctx: Any, directory: str) -> None:
    """Creates the scaffold of an application"""
