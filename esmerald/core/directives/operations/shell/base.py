import select
import sys

import click
from lilya.cli.directives.operations.shell.base import handle_lifespan_events, run_shell
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
