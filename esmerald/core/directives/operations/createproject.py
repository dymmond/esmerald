"""
Client to interact with Saffier models and migrations.
"""

from typing import Any

import click


@click.option(
    "-n",
    "--name",
    help=("Name of the project"),
)
@click.option(
    "-d",
    "--directory",
    default=None,
    help=("Directory to place the project scaffold"),
)
@click.command(context_settings={"ignore_unknown_options": True})
def create_project(name: str, directory: str) -> None:
    """Creates the scaffold of a project"""
