from __future__ import annotations

from typing import Annotated

from sayer import Argument, Option, command, error, success

from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.directives.operations._constants import SECRET_KEY_INSECURE_PREFIX
from esmerald.core.directives.templates import TemplateDirective
from esmerald.utils.crypto import get_random_secret_key


@command(name="createproject")  # type: ignore
def create_project(
    name: Annotated[str, Argument(help="The name of the project to create.")],
    verbosity: Annotated[int, Option(1, "-v", help="Verbosity level for the output.")],
    with_deployment: Annotated[
        bool,
        Option(False, help="Creates a project with base deployment files.", show_default=True),
    ],
    deployment_folder_name: Annotated[
        str,
        Option(
            "deployment",
            help="The name of the folder for the deployment files.",
            show_default=True,
        ),
    ],
    with_structure: Annotated[
        bool,
        Option(
            False,
            help="Creates a project with a given structure of folders and files.",
            show_default=True,
        ),
    ],
    simple: Annotated[
        bool,
        Option(
            False,
            "-s",
            help="Generates a project in simple mode.",
            show_default=True,
        ),
    ],
    edgy: Annotated[
        bool,
        Option(
            False,
            "-e",
            help="Generates a project with configurations for Edgy ORM.",
            show_default=True,
        ),
    ],
) -> None:
    """
    Creates the scaffold of a project.

    How to run: `esmerald createproject <NAME>`

    Example: `esmerald createproject myproject`
    """
    options = {
        "secret_key": SECRET_KEY_INSECURE_PREFIX + get_random_secret_key(),
        "verbosity": verbosity,
        "with_deployment": with_deployment,
        "deployment_folder_name": deployment_folder_name,
        "simple": simple,
        "edgy": edgy,
    }
    directive = TemplateDirective()

    try:
        directive.handle("project", name=name, **options)
        success(f" Project {name} generated successfully!")
    except DirectiveError as e:
        error(str(e))
