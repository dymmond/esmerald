from __future__ import annotations

from lilya.context import g
from sayer import command, success

from esmerald import directive
from tests.cli.global_context.objects import Test  # noqa: F401


@directive
@command
async def run_test():
    """
    Test directive for creating a user
    """
    g.name = "Esmerald from global"

    name = Test().get_name()
    success(f"Context successfully set to {name}.")
