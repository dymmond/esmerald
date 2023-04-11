"""
Client to interact with Saffier models and migrations.
"""
import sys
import typing

import click

from esmerald.core.directives.constants import APP_PARAMETER, HELP_PARAMETER
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations import create_app, create_project


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
        directive = DirectiveEnv()
        app_env = directive.load_from_env(path=path)
        ctx.obj = app_env.app
        ctx.path = app_env.path


esmerald_cli.add_command(create_project, name="create-project")
esmerald_cli.add_command(create_app, name="create-app")
