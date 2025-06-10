from collections.abc import Callable
from typing import Any


def directive(func: Callable[..., Any]) -> Callable:
    """
    Marks a function-based Sayer CLI command as a custom Esmerald directive.
    This decorator is used to register user-defined CLI commands that follow the
    function-based directive pattern. It tags the command with a special attribute
    (__is_custom_directive__ = True) so Esmerald's CLI system can treat it differently
    from internal class-based directives.
    The command must already be decorated with `@command` from Sayer before applying this.
    Example usage:
        @directive
        @command(name="create")
        async def create(name: Annotated[str, Option(help="Your name")]):
            ...
    Returns:
        Callable: The original command object, with a marker and registered in the main CLI.
    """
    from esmerald.core.directives.cli import esmerald_cli

    func.__is_custom_directive__ = True
    func.get_help = esmerald_cli.get_help
    esmerald_cli.add_command(func)

    return func
