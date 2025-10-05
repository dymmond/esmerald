import typing
from pathlib import Path
from typing import TypeVar

import click
from sayer import Option, Sayer

from ravyn import __version__  # noqa
from ravyn.core.directives.groups import DirectiveGroup
from ravyn.core.directives.operations._constants import RAVYN_SETTINGS_MODULE  # noqa
from ravyn.core.directives.operations.createapp import create_app as create_app  # noqa
from ravyn.core.directives.operations.createdeployment import (
    create_deployment as create_deployment,  # noqa
)
from ravyn.core.directives.operations.createproject import (
    create_project as create_project,  # noqa
)
from ravyn.core.directives.operations.list import directives as directives  # noqa
from ravyn.core.directives.operations.mail import mail as mail  # noqa
from ravyn.core.directives.operations.run import run as run  # noqa
from ravyn.core.directives.operations.runserver import runserver as runserver  # noqa
from ravyn.core.directives.operations.shell import shell as shell  # noqa
from ravyn.core.directives.operations.show_urls import show_urls as show_urls  # noqa
from ravyn.core.directives.utils import get_custom_directives_to_cli

T = TypeVar("T")


help_text = """
Ravyn command line tool allowing to run Ravyn native directives or
project unique and specific directives by passing the `-n` parameter.

How to run Ravyn native: `ravyn createproject <NAME>`. Or any other Ravyn native command.

    Example: `ravyn createproject myapp`


How to run custom directives: `ravyn --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

    Example: `ravyn --app myapp:app run -n createsuperuser`

"""

ravyn_cli = Sayer(
    help=help_text,
    add_version_option=True,
    version=__version__,
    group_class=DirectiveGroup,
)


@ravyn_cli.callback(invoke_without_command=True)
def ravyn_callback(
    ctx: click.Context,
    app: typing.Annotated[
        str,
        Option(
            required=False,
            help="Module path to the Ravyn application. In a module:path format.",
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


ravyn_cli.add_command(directives)
ravyn_cli.add_command(show_urls)
ravyn_cli.add_command(runserver)
ravyn_cli.add_command(run)
ravyn_cli.add_command(create_project)
ravyn_cli.add_command(create_app)
ravyn_cli.add_command(create_deployment)
ravyn_cli.add_command(shell)
ravyn_cli.add_app("mail", mail)

# Load custom directives if any
application_directives = get_custom_directives_to_cli(str(Path.cwd()))

# Add application directives to the CLI
if application_directives:
    for _, command in application_directives.items():
        if isinstance(command, Sayer):
            ravyn_cli.add_custom_command(command, command._group.name)
        else:
            ravyn_cli.add_custom_command(command)
