import inspect
import os
import sys
import typing
from functools import wraps
from typing import Callable, TypeVar

import click
from sayer import Argument, Option, Sayer, error
from sayer.core.groups.sayer import SayerGroup

from esmerald import __version__
from esmerald.core.directives.constants import (
    EXCLUDED_DIRECTIVES,
    HELP_PARAMETER,
    IGNORE_DIRECTIVES,
)
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations._constants import ESMERALD_SETTINGS_MODULE  # noqa
from esmerald.core.directives.operations.createapp import create_app as create_app  # noqa
from esmerald.core.directives.operations.createdeployment import (
    create_deployment as create_deployment,  # noqa
)
from esmerald.core.directives.operations.createproject import (
    create_project as create_project,  # noqa
)
from esmerald.core.directives.operations.list import directives as directives  # noqa
from esmerald.core.directives.operations.run import run as run  # noqa
from esmerald.core.directives.operations.runserver import runserver as runserver  # noqa
from esmerald.core.directives.operations.shell import shell as shell  # noqa
from esmerald.core.directives.operations.show_urls import show_urls as show_urls  # noqa

T = TypeVar("T")


class DirectiveGroup(SayerGroup):
    """Custom directive group to handle with the context and directives commands"""

    def add_command(self, cmd: click.Command, name: str | None = None) -> None:
        if cmd.callback:
            cmd.callback = self.wrap_args(cmd.callback)
        return super().add_command(cmd, name)

    def wrap_args(self, func: Callable[..., T]) -> Callable[..., T]:
        original = inspect.unwrap(func)
        params = inspect.signature(original).parameters

        @wraps(func)
        def wrapped(ctx: click.Context, /, *args: typing.Any, **kwargs: typing.Any) -> T:
            scaffold = ctx.ensure_object(DirectiveEnv)
            if "env" in params:
                kwargs["env"] = scaffold
            return func(*args, **kwargs)

        # click.pass_context makes sure that 'ctx' is the first argument
        return click.pass_context(wrapped)

    def process_settings(self, ctx: click.Context) -> None:
        """
        Process the settings context" if any is passed.

        Exports any ESMERALD_SETTINGS_MODULE to the environment if --settings is passed and exists
        as one of the params of any subcommand.
        """
        args = [*ctx.protected_args, *ctx.args]
        cmd_name, cmd, args = self.resolve_command(ctx, args)
        sub_ctx = cmd.make_context(cmd_name, args, parent=ctx)

        settings = sub_ctx.params.get("settings", None)
        if settings:
            settings_module: str = os.environ.get(ESMERALD_SETTINGS_MODULE, settings)
            os.environ.setdefault(ESMERALD_SETTINGS_MODULE, settings_module)

    def invoke(self, ctx: click.Context) -> typing.Any:
        """
        Directives can be ignored depending of the functionality from what is being
        called.
        """
        path = ctx.params.get("app", None)

        # Process any settings
        self.process_settings(ctx)

        if HELP_PARAMETER not in sys.argv and not any(
            value in sys.argv for value in EXCLUDED_DIRECTIVES
        ):
            try:
                directive = DirectiveEnv()
                app_env = directive.load_from_env(path=path)
                ctx.obj = app_env
            except OSError as e:
                if not any(value in sys.argv for value in IGNORE_DIRECTIVES):
                    error(str(e))
                    sys.exit(1)
        return super().invoke(ctx)


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
    name: typing.Annotated[str, Argument(help="The directive name.")],
    app: typing.Annotated[
        str,
        Option(
            required=False,
            help="Module path to the Esmerald application. In a module:path format.",
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
