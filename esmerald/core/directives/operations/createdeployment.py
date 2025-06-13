from __future__ import annotations

from typing import Annotated

from sayer import Argument, Option, command, error, success

from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.directives.templates import TemplateDirective


@command(name="createdeployment")  # type: ignore
def create_deployment(
    name: Annotated[str, Argument(help="The name of the current project.")],
    verbosity: Annotated[
        int, Option(1, "-v", help="Displays the files generated", show_default=True)
    ],
    deployment_folder_name: Annotated[
        str,
        Option(
            default="deployment",
            help="The name of the folder for the deployment files.",
            show_default=True,
        ),
    ],
) -> None:
    """
    Generates the scaffold for the deployment of an Esmerald application.

    The scaffold contains the configurations for docker, nginx, supervisor and gunicorn.

    The configurations should be adapted accordingly.
    The parameter <NAME> corresponds to the name of the
    project where the deployment should be placed.

    How to run: `esmerald createdeployment <NAME>`

    Example: `esmerald createdeployment myproject`
    """
    options = {
        "verbosity": verbosity,
        "deployment_folder_name": deployment_folder_name,
    }
    directive = TemplateDirective()

    try:
        directive.handle("deployment", name=name, **options)
        success(f" Deployment for {name} generated successfully!")
    except DirectiveError as e:
        error(str(e))
