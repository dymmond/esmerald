from collections.abc import Callable
from typing import Any


def directive(
    func: Callable[..., Any] | None = None,
    *,
    display_in_cli: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Marks a function-based Sayer CLI command as a custom Ravyn directive.
    This decorator is used to register user-defined CLI commands that follow the
    function-based directive pattern. It tags the command with a special attribute
    (__is_custom_directive__ = True) so Ravyn's CLI system can treat it differently
    from internal class-based directives.
    The command must already be decorated with `@command` from Sayer before applying this.
    Example usage:
        @directive(display_in_cli=True)
        @command(name="create")
        async def create(name: Annotated[str, Option(help="Your name")]):
            ...
    Returns:
        Callable: The original command object, with a marker and registered in the main CLI.
    """

    def wrapper(f: Callable[..., Any]) -> Callable[..., Any]:
        f.__is_custom_directive__ = True
        f.__display_in_cli__ = display_in_cli
        return f

    if func is not None:
        return wrapper(func)

    return wrapper
