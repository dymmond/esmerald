import inspect
import os
import sys
import typing
from functools import wraps

import click

from esmerald.core.directives.constants import (
    APP_PARAMETER,
    EXCLUDED_DIRECTIVES,
    HELP_PARAMETER,
    IGNORE_DIRECTIVES,
)
from esmerald.core.directives.env import DirectiveEnv
from esmerald.core.directives.operations import (
    create_app,
    create_project,
    list,
    run,
    runserver,
    show_urls,
)
from esmerald.core.directives.operations._constants import ESMERALD_SETTINGS_MODULE
from esmerald.core.terminal.print import Print
from esmerald.exceptions import EnvironmentError

printer = Print()


class DirectiveGroup(click.Group):
    """Custom directive group to handle with the context and directives commands"""

    def add_command(self, cmd: click.Command, name: typing.Optional[str] = None) -> None:
        if cmd.callback:
            cmd.callback = self.wrap_args(cmd.callback)
        return super().add_command(cmd, name)

    def wrap_args(self, func: typing.Any) -> typing.Any:
        params = inspect.signature(func).parameters

        @wraps(func)
        def wrapped(ctx: click.Context, /, *args: typing, **kwargs: typing) -> typing:
            scaffold = ctx.ensure_object(DirectiveEnv)
            if "env" in params:
                kwargs["env"] = scaffold
            return func(*args, **kwargs)

        return click.pass_context(wrapped)

    def process_settings(self, ctx: click.Context):
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
        path = ctx.params.get("path", None)

        # Process any settings
        self.process_settings(ctx)

        if HELP_PARAMETER not in sys.argv and not any(
            value in sys.argv for value in EXCLUDED_DIRECTIVES
        ):
            try:
                directive = DirectiveEnv()
                app_env = directive.load_from_env(path=path)
                ctx.obj = app_env
            except EnvironmentError as e:
                if not any(value in sys.argv for value in IGNORE_DIRECTIVES):
                    printer.write_error(str(e))
                    sys.exit(1)
        return super().invoke(ctx)


@click.group(
    cls=DirectiveGroup,
)
@click.option(
    APP_PARAMETER,
    "path",
    help="Module path to the application to generate the migrations. In a module:path formatyping.",
)
@click.option("--n", "name", help="The directive name to run.")
@click.pass_context
def esmerald_cli(
    ctx: click.Context,
    path: typing.Optional[str],
    name: str,
) -> None:
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
esmerald_cli.add_command(runserver)
