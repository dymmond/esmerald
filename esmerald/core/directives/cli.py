import os
import sys
import typing

import click

from esmerald.core.directives.constants import APP_PARAMETER, ESMERALD_DISCOVER_APP, HELP_PARAMETER
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations import create_app, create_project, list, run, show_urls
from esmerald.core.terminal.print import Print
from esmerald.exceptions import EnvironmentError

printer = Print()


class DirectiveGroup(click.Group):
    """Custom directive group to handle with the context objects"""

    def invoke(self, ctx: click.Context) -> typing.Any:
        path = ctx.params.get("path", None)
        if HELP_PARAMETER not in sys.argv:
            if APP_PARAMETER in sys.argv or os.getenv(ESMERALD_DISCOVER_APP) is not None:
                try:
                    directive = DirectiveEnv()
                    app_env = directive.load_from_env(path=path)
                    ctx.obj = app_env
                except EnvironmentError as e:
                    printer.write_error(str(e))
                    sys.exit(1)
        return super().invoke(ctx)


@click.group(cls=DirectiveGroup)
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

    How to run Esmerald native: `esmerald createproject <NAME>`. Or any other Esmerald native command.

        Example: `esmerald createproject myapp`


    How to run custom directives: `esmerald --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

        Example: `esmerald --app myapp:app run -n createsuperuser`

    """
    ...


esmerald_cli.add_command(list)
esmerald_cli.add_command(show_urls)
esmerald_cli.add_command(run)
esmerald_cli.add_command(create_project)
esmerald_cli.add_command(create_app)
