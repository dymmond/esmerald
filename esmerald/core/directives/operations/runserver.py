import os
import sys
from typing import TYPE_CHECKING, Union

import click

from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.terminal import OutputColour, Print, Terminal

if TYPE_CHECKING:
    pass

printer = Print()
terminal = Terminal()


@click.option(
    "-p",
    "--port",
    type=int,
    default=8000,
    help="Port to run the development server.",
    show_default=True,
)
@click.option(
    "-r",
    "--reload",
    type=bool,
    default=True,
    help="Reload server on file changes.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--host",
    type=str,
    default="localhost",
    help="Server host. Tipically localhost.",
    show_default=True,
)
@click.option(
    "--debug",
    type=bool,
    default=True,
    help="Start the application in debug mode.",
    show_default=True,
    is_flag=True,
)
@click.option(
    "--log-level",
    type=str,
    default="debug",
    help="What log level should uvicorn run.",
    show_default=True,
)
@click.option(
    "--lifespan",
    type=str,
    default="on",
    help="Enable lifespan events.",
    show_default=True,
)
@click.option(
    "--settings", type=str, help="Any custom settings to be initialised.", required=False
)
@click.command(name="runserver")
def runserver(
    env: DirectiveEnv,
    port: int,
    reload: bool,
    host: str,
    debug: bool,
    log_level: str,
    lifespan: str,
    settings: Union[str, None] = None,
) -> None:
    """Starts the Esmerald development server.

    The --app can be passed in the form of <module>.<submodule>:<app> or be set
    as environment variable ESMERALD_DEFAULT_APP.

    Alternatively, if none is passed, Esmerald will perform the application discovery.

    It is strongly advised not to run this command in any other environment but development.
    This was designed to facilitate the development environment and should not be used in production.

    How to run: `esmerald runserver`
    """
    if getattr(env, "app", None) is None:
        error = (
            "You cannot specify a custom directive without specifying the --app or setting "
            "ESMERALD_DEFAULT_APP environment variable."
        )
        printer.write_error(error)
        sys.exit(1)

    if settings is not None:
        os.environ.setdefault("ESMERALD_SETTINGS_MODULE", settings)

    try:
        import uvicorn
    except ImportError:
        raise DirectiveError(
            detail="Uvicorn needs to be installed to run Esmerald `runserver`."
        ) from None

    server_environment: str = ""
    if os.environ.get("ESMERALD_SETTINGS_MODULE"):
        from esmerald.conf import settings as esmerald_settings

        server_environment = f"{esmerald_settings.environment} "
    app = env.app

    warning = "Do not run this in production. This is for development purposes only."
    printer.write_warning(warning)

    message = terminal.write_info(
        f"Starting {server_environment}server @ {host}",
        colour=OutputColour.BRIGHT_CYAN,
    )
    terminal.rule(message, align="center")

    if os.environ.get("ESMERALD_SETTINGS_MODULE"):
        custom_message = f"'{os.environ['ESMERALD_SETTINGS_MODULE']}'"
        terminal.rule(custom_message, align="center")

    if debug:
        app.debug = debug

    uvicorn.run(
        app=env.path,
        port=port,
        host=host,
        reload=reload,
        lifespan=lifespan,  # type: ignore
        log_level=log_level,
    )
