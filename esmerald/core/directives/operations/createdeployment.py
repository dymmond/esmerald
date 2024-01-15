import click

from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.directives.templates import TemplateDirective
from esmerald.core.terminal import Print

printer = Print()


@click.option("-v", "--verbosity", default=1, type=int, help="Displays the files generated")
@click.option(
    "--deployment-folder-name",
    default="deployment",
    show_default=True,
    type=str,
    help="The name of the folder for the deployment files.",
)
@click.argument("name", type=str)
@click.command(name="createdeployment")
def create_deployment(name: str, verbosity: int, deployment_folder_name: str) -> None:
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
        printer.write_success(f"Deployment for {name} generated successfully!")
    except DirectiveError as e:
        printer.write_error(str(e))
