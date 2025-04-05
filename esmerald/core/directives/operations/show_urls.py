import inspect
import os
import sys
from typing import TYPE_CHECKING, Any, Optional, Union

import click
from lilya._internal._path import clean_path
from rich.console import Console
from rich.table import Table

from esmerald import Gateway, Router
from esmerald.core.directives.constants import ESMERALD_DISCOVER_APP
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.terminal import OutputColour, Print, Terminal
from esmerald.routing.apis.base import View
from esmerald.utils.enums import HttpMethod

if TYPE_CHECKING:
    from lilya.routing import BasePath

    from esmerald.applications import ChildEsmerald, Esmerald

printer = Print()
writer = Terminal()
console = Console()

DOCS_ELEMENTS = [
    "/swagger",
    "/redoc",
    "/openapi.json",
    "/openapi.yaml",
    "/openapi.yml",
    "/elements",
]


def get_http_verb(mapping: Any) -> str:
    if getattr(mapping, "get", None):
        return HttpMethod.GET.value
    elif getattr(mapping, "post", None):
        return HttpMethod.POST.value
    elif getattr(mapping, "put", None):
        return HttpMethod.PUT.value
    elif getattr(mapping, "patch", None):
        return HttpMethod.PATCH.value
    elif getattr(mapping, "delete", None):
        return HttpMethod.DELETE.value
    elif getattr(mapping, "header", None):
        return HttpMethod.HEAD.value
    elif getattr(mapping, "trace", None):
        return HttpMethod.TRACE.value
    elif getattr(mapping, "options", None):
        return HttpMethod.OPTIONS.value
    return HttpMethod.GET.value


@click.command(name="show_urls")
def show_urls(env: DirectiveEnv) -> None:
    """Shows the information regarding the urls of a given application

    How to run: `esmerald show_urls`

    Example: `esmerald show_urls`
    """
    if os.getenv(ESMERALD_DISCOVER_APP) is None and getattr(env, "app", None) is None:
        error = (
            "You cannot specify a custom directive without specifying the --app or setting "
            "ESMERALD_DEFAULT_APP environment variable."
        )
        printer.write_error(error)
        sys.exit(1)

    app = env.app
    table = Table(title=app.app_name)
    table = get_routes_table(app, table)
    printer.write(table)


def get_routes_table(app: Optional[Union["Esmerald", "ChildEsmerald"]], table: Table) -> Table:
    """Prints the routing system"""
    table.add_column("Path", style=OutputColour.GREEN, vertical="middle")
    table.add_column("Path Parameters", style=OutputColour.BRIGHT_CYAN, vertical="middle")
    table.add_column("Name & Path Lookup", style=OutputColour.CYAN, vertical="middle")
    table.add_column("Type", style=OutputColour.YELLOW, vertical="middle")
    table.add_column("HTTP Methods", style=OutputColour.RED, vertical="middle")

    def parse_routes(
        app: Optional[Union["Esmerald", "ChildEsmerald", "Router", "BasePath"]],
        table: Table,
        route: Optional[Any] = None,
        prefix: Optional[str] = "",
    ) -> None:
        if getattr(app, "routes", None) is None:
            return

        for route in app.routes:  # type: ignore
            if isinstance(route, Gateway):
                # Path
                path = clean_path(prefix + route.path)

                if any(element in path for element in DOCS_ELEMENTS):
                    continue

                # Type
                if not isinstance(route.handler, View):
                    if inspect.iscoroutinefunction(route.handler.fn):
                        fn_type = "async"
                    else:
                        fn_type = "sync"

                # Http methods
                names = route.handler.get_lookup_path()

                # We need to escape the character ':' to avoid the error
                # of the table not being able to render the string
                route_name = ":".join(names)

                http_methods = ", ".join(sorted(route.methods))
                parameters = ", ".join(sorted(route.stringify_parameters))
                table.add_row(path, parameters, route_name, fn_type, http_methods)
                continue

            route_app = getattr(route, "app", None)
            if not route_app:
                continue

            path = clean_path(prefix + route.path)  # type: ignore
            if any(element in path for element in DOCS_ELEMENTS):
                continue
            parse_routes(route, table, prefix=f"{path}")

    parse_routes(app, table)
    return table
