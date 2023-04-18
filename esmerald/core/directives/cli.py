import inspect
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
from esmerald.core.terminal.print import Print
from esmerald.exceptions import EnvironmentError

printer = Print()


class DirectiveGroup(click.Group):
    """Custom directive group to handle with the context objects"""

    def __init__(
        self,
        name: typing.Optional[str] = None,
        commands: typing.Optional[
            typing.Union[typing.Dict[str, click.Command], typing.Sequence[click.Command]]
        ] = None,
        **attrs: typing.Any,
    ) -> None:
        self.group_class = DirectiveGroup
        super().__init__(name, commands, **attrs)

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

    def invoke(self, ctx: click.Context) -> typing.Any:
        """
        Directives can be ignored depending of the functionality from what is being
        called.
        """
        path = ctx.params.get("path", None)

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
@click.option(
    "--settings",
    type=str,
    help="Start the server with specific settings.",
    required=False,
)
@click.pass_context
def esmerald_cli(ctx: click.Context, path: typing.Optional[str], name: str, settings: str) -> None:
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
