"""
Client to interact with Saffier models and migrations.
"""
import sys
import typing

import click

from esmerald.core.directives.constants import APP_PARAMETER, HELP_PARAMETER
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations import create_app, create_project, list, run
from esmerald.core.terminal.print import Print
from esmerald.exceptions import EnvironmentError

printer = Print()


@click.group()
@click.option(
    APP_PARAMETER,
    "path",
    help="Module path to the application to generate the migrations. In a module:path format.",
)
@click.option("--n", "name", help="The directive name to run.")
@click.pass_context
def esmerald_cli(ctx: click.Context, path: typing.Optional[str], name: str) -> None:
    """
    Esmerald command line tool allowing to run Esmerald native directives or
    project unique and specific directives by passing the `-n` parameter.

    How to run Esmerald native: `esmerald-admin createproject <NAME>`. Or any other Esmerald native command.

        Example: `esmerald-admin createproject myapp`


    How to run custom directives: `esmerald-admin --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

        Example: `esmerald-admin --app myapp:app run -n createsuperuser`

    """
    if HELP_PARAMETER not in sys.argv:
        if APP_PARAMETER in sys.argv:
            try:
                directive = DirectiveEnv()
                app_env = directive.load_from_env(path=path)
                ctx.obj = app_env
            except EnvironmentError as e:
                printer.write_error(str(e))
                sys.exit(1)


esmerald_cli.add_command(list)
esmerald_cli.add_command(create_project)
esmerald_cli.add_command(create_app)
esmerald_cli.add_command(run)
