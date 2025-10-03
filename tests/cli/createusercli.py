from __future__ import annotations

from typing import Annotated

from sayer import Option, command, success

from ravyn.core.directives.decorator import directive


@directive(display_in_cli=True)
@command(name="create-user")
async def create(
    name: Annotated[str, Option(required=True)],
):
    """
    Test directive for creating a user
    """

    success(f"Superuser {name} created successfully.")
