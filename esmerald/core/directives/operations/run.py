"""
Client to interact with Saffier models and migrations.
"""

import sys
from collections import defaultdict
from typing import Any

import click

from esmerald.core.directives.operations._constants import PATH
from esmerald.core.directives.utils import (
    fetch_directive,
    get_application_directives,
    get_directives,
)
from esmerald.core.terminal.print import Print

printer = Print()

from esmerald.core.directives.operations._constants import PATH


@click.option(
    "-n",
    "--name",
    required=True,
    help=("The name of the custom directive to run"),
)
@click.command(name="run")
@click.pass_context
def run(ctx: Any, name: str) -> None:
    """
    Runs every single custom directive in the system.

    How to run: `esmerald-admin --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

        Example: `esmerald-admin --app myapp:app run -n createsuperuser`
    """
    if name is not None and getattr(ctx, "obj", None) is None:
        error = (
            "You cannot specify a custom directive without specifying the --app or setting "
            "ESMERALD_DEFAULT_APP environment variable."
        )
        printer.write_error(error)
        sys.exit(1)

    directive = fetch_directive(name, ctx.obj.command_path, True)
    if not directive:
        # directive = fetch_directive(name, PATH)
        printer.write_error("Unknown directive: %r" % name)
        sys.exit(1)
