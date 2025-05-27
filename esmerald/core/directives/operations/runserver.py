import os
import sys
from typing import TYPE_CHECKING, Annotated

from sayer import Option, command, error, warning

from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.terminal import OutputColour, Terminal

if TYPE_CHECKING:
    pass

terminal = Terminal()


@command
def runserver(
    env: DirectiveEnv,
    port: Annotated[
        int, Option(8000, "-p", help="Port to run the development server.", show_default=True)
    ],
    reload: Annotated[
        bool, Option(True, "-r", help="Reload server on file changes.", show_default=True)
    ],
    host: Annotated[
        str, Option(default="localhost", help="Host to run the server on.", show_default=True)
    ],
    debug: Annotated[
        bool, Option(default=True, help="Run the server in debug mode.", show_default=True)
    ],
    log_level: Annotated[
        str, Option(default="debug", help="Log level for the server.", show_default=True)
    ],
    lifespan: Annotated[
        str, Option(default="on", help="Enable lifespan events.", show_default=True)
    ],
    settings: Annotated[
        str | None,
        Option(help="Any custom settings to be initialised.", required=False, show_default=False),
    ],
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
        error(
            "You cannot specify a custom directive without specifying the --app or setting "
            "ESMERALD_DEFAULT_APP environment variable."
        )
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

    warning("Do not run this in production. This is for development purposes only.")
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
