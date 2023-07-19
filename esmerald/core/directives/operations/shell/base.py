import select
import sys
from typing import Any, Callable, Optional, Sequence

import click
import nest_asyncio

from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations.shell.enums import ShellOption
from esmerald.routing.events import AyncLifespanContextManager
from esmerald.utils.sync import execsync


@click.option(
    "--kernel",
    default="ipython",
    type=click.Choice(["ipython", "ptpython"]),
    help="Which shell should start.",
    show_default=True,
)
@click.command()
def shell(env: DirectiveEnv, kernel: bool) -> None:
    """
    Starts an interactive ipython shell with all the models
    and important python libraries.
    """
    if (
        sys.platform != "win32"
        and not sys.stdin.isatty()
        and select.select([sys.stdin], [], [], 0)[0]
    ):
        exec(sys.stdin.read(), globals())
        return

    on_startup = getattr(env.app, "on_startup", [])
    on_shutdown = getattr(env.app, "on_shutdown", [])
    lifespan = getattr(env.app, "lifespan", None)
    lifespan = handle_lifespan_events(
        on_startup=on_startup, on_shutdown=on_shutdown, lifespan=lifespan
    )
    execsync(run_shell)(env.app, lifespan, kernel)  # type: ignore
    return None


async def run_shell(app: Any, lifespan: Any, kernel: str) -> None:
    """Executes the database shell connection"""

    async with lifespan(app):
        if kernel == ShellOption.IPYTHON:
            from esmerald.core.directives.operations.shell.ipython import get_ipython

            ipython_shell = get_ipython(app=app)
            nest_asyncio.apply()
            ipython_shell()
        else:
            from esmerald.core.directives.operations.shell.ptpython import get_ptpython

            ptpython = get_ptpython(app=app)
            nest_asyncio.apply()
            ptpython()


def handle_lifespan_events(
    on_startup: Optional[Sequence[Callable]] = None,
    on_shutdown: Optional[Sequence[Callable]] = None,
    lifespan: Optional[Any] = None,
) -> Any:
    """Handles with the lifespan events in the new Starlette format of lifespan.
    This adds a mask that keeps the old `on_startup` and `on_shutdown` events variable
    declaration for legacy and comprehension purposes and build the async context manager
    for the lifespan.
    """
    if lifespan:
        return lifespan
    return AyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
