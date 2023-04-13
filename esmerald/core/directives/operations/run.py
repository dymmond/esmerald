"""
Client to interact with Saffier models and migrations.
"""

import sys
from collections import defaultdict
from typing import Any

import click

from esmerald.core.directives.utils import fetch_directive
from esmerald.core.terminal.print import Print

printer = Print()


@click.command(
    name="run",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.option(
    "--directive",
    "directive",
    required=True,
    help=("The name of the custom directive to run"),
)
@click.argument("directive_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx: Any, directive: str, directive_args: Any) -> None:
    """
    Runs every single custom directive in the system.

    How to run: `esmerald-admin --app <APP-LOCATION> run -n <DIRECTIVE NAME> <ARGS>`.

        Example: `esmerald-admin --app myapp:app run -n createsuperuser`
    """
    name = directive
    if name is not None and getattr(ctx, "obj", None) is None:
        error = (
            "You cannot specify a custom directive without specifying the --app or setting "
            "ESMERALD_DEFAULT_APP environment variable."
        )
        printer.write_error(error)
        sys.exit(1)

    # Loads the directive object
    directive = fetch_directive(name, ctx.obj.command_path, True)
    if not directive:
        printer.write_error("Unknown directive: %r" % name)
        sys.exit(1)

    # Execute the directive
    # The arguments for the directives start at the position 6
    if sys.argv[6:] in (["--info"],):
        directive.print_help(sys.argv[0], sys.argv[5])
    else:
        directive.execute_from_command(sys.argv[:])
