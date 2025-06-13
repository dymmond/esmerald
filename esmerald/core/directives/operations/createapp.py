from __future__ import annotations

from typing import Annotated

from sayer import Argument, Option, command, error, success

from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.directives.operations._constants import SECRET_KEY_INSECURE_PREFIX
from esmerald.core.directives.templates import TemplateDirective
from esmerald.utils.crypto import get_random_secret_key


@command(name="createapp")  # type: ignore
def create_app(
    name: Annotated[str, Argument(help="The name of the app.")],
    verbosity: Annotated[int, Option(1, "-v", help="Displays the files generated")],
    with_basic_controller: Annotated[
        bool, Option(False, help="Should generate a basic controller")
    ],
    context: Annotated[
        bool,
        Option(
            False,
            help="Should generate an application with a controller, service, repository, dto.",
        ),
    ],
) -> None:
    """Creates the scaffold of an application

    How to run: `esmerald createapp <NAME>`

    Example: `esmerald createapp myapp`
    """
    options = {
        "secret_key": SECRET_KEY_INSECURE_PREFIX + get_random_secret_key(),
        "verbosity": verbosity,
        "with_basic_controller": with_basic_controller,
        "simple": False,
        "app_context": context,
    }
    directive = TemplateDirective()

    try:
        directive.handle("app", name=name, **options)
        success(f" App {name} generated successfully!")
    except DirectiveError as e:
        error(str(e))
