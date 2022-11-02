from typing import Any, Dict

from esmerald.core.management.templates import TemplateDirective
from esmerald.utils.crypto import get_random_secret_key

SECRET_KEY_INSECURE_PREFIX = "esmerald-insecure-"


class Directive(TemplateDirective):
    help = (
        "Creates an Esmerald project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide a project name."

    def handle(self, **options: Dict[str, Any]):
        project_name = options.pop("name")

        options["secret_key"] = SECRET_KEY_INSECURE_PREFIX + get_random_secret_key()
        super().handle("project", project_name, **options)
