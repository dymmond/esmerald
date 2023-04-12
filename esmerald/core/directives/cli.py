"""
Client to interact with Saffier models and migrations.
"""
import sys
import typing

import click
from rich.console import Console

from esmerald.core.directives.constants import APP_PARAMETER, HELP_PARAMETER
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations import create_app, create_project, list
from esmerald.exceptions import EnvironmentError

console = Console()


@click.group()
@click.option(
    APP_PARAMETER,
    "path",
    help="Module path to the application to generate the migrations. In a module:path format.",
)
@click.pass_context
def esmerald_cli(ctx: click.Context, path: typing.Optional[str]) -> None:
    """Performs database migrations"""
    if HELP_PARAMETER not in sys.argv:
        if APP_PARAMETER in sys.argv:
            try:
                directive = DirectiveEnv()
                app_env = directive.load_from_env(path=path)
                ctx.obj = app_env.app
                ctx.path = app_env.path
            except EnvironmentError as e:
                console.print(f"[red]{str(e)}[/red]")
                sys.exit(1)


esmerald_cli.add_command(list, name="directives")
esmerald_cli.add_command(create_project)
esmerald_cli.add_command(create_app)
