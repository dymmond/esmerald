import asyncio
import select
import sys
from collections.abc import Sequence
from contextvars import copy_context
from typing import Any, Callable, Union

import click
from lilya._internal._events import AsyncLifespanContextManager
from lilya.cli.directives.operations.shell.enums import ShellOption
from lilya.compat import run_sync

from esmerald.core.directives.env import DirectiveEnv


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
    run_sync(run_shell(env.app, lifespan, kernel))  # type: ignore
    return None


async def run_shell(app: Any, lifespan: Any, kernel: str) -> None:
    """Executes the database shell connection"""

    async with lifespan(app):
        if kernel == ShellOption.IPYTHON:
            from esmerald.core.directives.operations.shell.ipython import get_ipython

            ipython_shell = get_ipython(app=app)
            await asyncio.to_thread(copy_context().run, ipython_shell)
        else:
            from esmerald.core.directives.operations.shell.ptpython import get_ptpython

            ptpython = get_ptpython(app=app)
            await asyncio.to_thread(copy_context().run, ptpython)


def handle_lifespan_events(
    on_startup: Union[Sequence[Callable], None] = None,
    on_shutdown: Union[Sequence[Callable], None] = None,
    lifespan: Union[Any, None] = None,
) -> Any:
    if lifespan:
        return lifespan
    return AsyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
