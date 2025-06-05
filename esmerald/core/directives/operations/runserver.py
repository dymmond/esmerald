import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from rich.tree import Tree
from sayer import Option, command, error

from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.terminal import Terminal
from esmerald.core.terminal.utils import get_log_config, get_ui_toolkit

if TYPE_CHECKING:
    pass

terminal = Terminal()


def get_app_tree(module_paths: list[Path], discovery_file: str) -> Tree:
    """
    Generates a tree structure representing the application modules.
    """
    root = module_paths[0]
    name = f"{root.name}" if root.is_file() else f"📁 {root.name}"

    root_tree = Tree(name)

    if root.is_dir():
        init_path = root / "__init__.py"
        if init_path.is_file():
            root_tree.add("[dim]__init__.py[/dim]")
            root_tree.add(f"[dim]{discovery_file}[/dim]")

    tree = root_tree
    for sub_path in module_paths[1:]:
        sub_name = f"{sub_path.name}" if sub_path.is_file() else f"📁 {sub_path.name}"
        tree = tree.add(sub_name)
        if sub_path.is_dir():
            tree.add("[dim]__init__.py[/dim]")
            tree.add(f"[dim]{discovery_file}[/dim]")

    return root_tree


@command
def runserver(
    env: DirectiveEnv,
    port: Annotated[int, Option(8000, "-p", help="Port to run the development server.", show_default=True)],
    reload: Annotated[bool, Option(True, "-r", help="Reload server on file changes.", show_default=True)],
    host: Annotated[str, Option(default="localhost", help="Host to run the server on.", show_default=True)],
    debug: Annotated[bool, Option(default=True, help="Run the server in debug mode.", show_default=True)],
    log_level: Annotated[str, Option(default="debug", help="Log level for the server.", show_default=True)],
    lifespan: Annotated[str, Option(default="on", help="Enable lifespan events.", show_default=True)],
    settings: Annotated[
        str | None,
        Option(help="Any custom settings to be initialised.", required=False, show_default=False),
    ],
    proxy_headers: Annotated[
        bool,
        Option(
            default=True,
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info.",
            show_default=True,
        ),
    ],
    workers: Annotated[
        int | None,
        Option(
            default=None,
            help="Use multiple worker processes. Mutually exclusive with the --reload flag.",
            required=False,
        ),
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
    with get_ui_toolkit() as toolkit:
        toolkit.print(
            "[gray50]Identifying package structures based on directories with [green]__init__.py[/green] files[/gray50]"
        )

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
            raise DirectiveError(detail="Uvicorn needs to be installed to run Esmerald `runserver`.") from None

        server_environment: str = ""
        if os.environ.get("ESMERALD_SETTINGS_MODULE"):
            from esmerald.conf import settings as esmerald_settings

            server_environment = f"{esmerald_settings.environment} "

        if not server_environment:
            server_environment = "development"

        toolkit.print_title(f"[green]Starting {server_environment} server[/green]", tag="Esmerald")
        toolkit.print(f"Importing from [green]{env.command_path}[/green]", tag="Esmerald")
        toolkit.print(f"Importing module '{env.path}'", tag="Esmerald")
        toolkit.print_line()

        root_tree = get_app_tree(env.module_info.module_paths, discovery_file=env.module_info.discovery_file)

        toolkit.print(root_tree, tag="module")
        toolkit.print_line()

        toolkit.print(
            "[green]The [bold]Esmerald[/bold] object is imported using the following code:[/green]",
            tag="code",
        )
        toolkit.print(
            f"[underline]from [bold]{env.module_info.module_import[0]}[/bold] import [bold]{env.module_info.module_import[1]}[/bold]",
            tag=env.module_info.module_import[1],
        )

        # For the text access
        url = f"http://{host}:{port}"
        docs = f"http://{host}:{port}/docs/swagger"

        toolkit.print_line()
        toolkit.print(
            f"Server started at [link={url}]{url}[/]",
            tag="server",
        )
        toolkit.print(
            f"Visit the docs at [link={docs}]{docs}[/]",
            tag="docs",
        )

        app = env.app

        if os.environ.get("ESMERALD_SETTINGS_MODULE"):
            custom_message = f"'{os.environ['ESMERALD_SETTINGS_MODULE']}'"
            toolkit.print(
                f"Using custom settings module: [bold][green]{custom_message}[/green][/bold]",
                tag="settings",
            )
        else:
            from esmerald.conf import settings as esmerald_settings

            toolkit.print(
                f"Using default settings module: [bold][green]{esmerald_settings.__class__.__module__}.Settings[/green][/bold]",
                tag="settings",
            )

        toolkit.print(
            "[yellow][bold]Remember, [bold]runserver is for development purposes[/bold]. For production, use a proper ASGI server.[/bold][/yellow]",
            tag="note",
        )
        toolkit.print_line()

        if debug:
            app.debug = debug

        uvicorn.run(
            app=env.path,
            port=port,
            host=host,
            reload=reload,
            lifespan=lifespan,  # type: ignore
            proxy_headers=proxy_headers,
            workers=workers,
            log_level=log_level,
            log_config=get_log_config(),
        )
