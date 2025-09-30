import typing
from pathlib import Path
from typing import TypeVar

import click
from sayer import Option, Sayer

from esmerald import __version__  # noqa
from esmerald.core.directives.groups import DirectiveGroup
from esmerald.core.directives.operations._constants import ESMERALD_SETTINGS_MODULE  # noqa
from esmerald.core.directives.operations.createapp import create_app as create_app  # noqa
from esmerald.core.directives.operations.createdeployment import (
    create_deployment as create_deployment,  # noqa
)
from esmerald.core.directives.operations.createproject import (
    create_project as create_project,  # noqa
)
from esmerald.core.directives.operations.list import directives as directives  # noqa
from esmerald.core.directives.operations.mail import mail as mail  # noqa
from esmerald.core.directives.operations.run import run as run  # noqa
from esmerald.core.directives.operations.runserver import runserver as runserver  # noqa
from esmerald.core.directives.operations.shell import shell as shell  # noqa
from esmerald.core.directives.operations.show_urls import show_urls as show_urls  # noqa
from esmerald.core.directives.utils import get_custom_directives_to_cli

T = TypeVar("T")


help_text = """
Esmerald command line tool allowing to run Esmerald native directives or
project unique and specific directives by passing the `-n` parameter.

How to run Esmerald native: `esmerald createproject <NAME>`. Or any other Esmerald native command.

    Example: `esmerald createproject myapp`


How to run custom directives: `esmerald --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

    Example: `esmerald --app myapp:app run -n createsuperuser`

"""

esmerald_cli = Sayer(
    help=help_text,
    add_version_option=True,
    version=__version__,
    group_class=DirectiveGroup,
)


@esmerald_cli.callback(invoke_without_command=True)
def esmerald_callback(
    ctx: click.Context,
    app: typing.Annotated[
        str,
        Option(
            required=False,
            help="Module path to the Esmerald application. In a module:path format.",
        ),
    ],
    path: typing.Annotated[
        str | None,
        Option(
            required=False,
            help="A path to a Python file or package directory with ([blue]__init__.py[/blue] files) containing a [bold]Lilya[/bold] app. If not provided, Lilya will try to discover.",
        ),
    ],
) -> None: ...


esmerald_cli.add_command(directives)
esmerald_cli.add_command(show_urls)
esmerald_cli.add_command(runserver)
esmerald_cli.add_command(run)
esmerald_cli.add_command(create_project)
esmerald_cli.add_command(create_app)
esmerald_cli.add_command(create_deployment)
esmerald_cli.add_command(shell)
esmerald_cli.add_app("mail", mail)

# Load custom directives if any
application_directives = get_custom_directives_to_cli(str(Path.cwd()))

# Add application directives to the CLI
if application_directives:
    for _, command in application_directives.items():
        if isinstance(command, Sayer):
            esmerald_cli.add_custom_command(command, command._group.name)
        else:
            esmerald_cli.add_custom_command(command)
