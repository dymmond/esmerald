"""
Client to interact with Saffier models and migrations.
"""

from collections import defaultdict
from typing import Any

import click

from esmerald.core.directives.operations._constants import PATH
from esmerald.core.directives.utils import get_directives
from esmerald.core.terminal import OutputColour, Terminal

EXCUDED_DIRECTIVES = ["list", "run"]


@click.command()
@click.pass_context
def list(ctx: Any) -> None:
    """
    Lists the available directives

    Goes through the Esmerald core native directives and given --app
    and lists all the available directives in the system.
    """
    output = Terminal()
    usage = [
        "",
        "Type '<directive> <subcommand> --help' for help on a specific subcommand.",
        "",
        "Available directives:",
    ]

    directives = get_directives(PATH)

    directives_dict = defaultdict(lambda: [])
    for name, app in directives.items():
        if app == "esmerald.core":
            app = "esmerald"
        else:
            app = app.rpartition(".")[-1]
        directives_dict[app].append(name)

    for app in sorted(directives_dict):
        usage.append("")
        usage.append(output.message("\\[%s]" % app, colour=OutputColour.SUCCESS))

        for name in sorted(directives_dict[app]):
            usage.append(output.message(f"    {name}", colour=OutputColour.INFO))
    output.write("\n".join(usage))
