from esmerald.core.management.templates import TemplateDirective


class Directive(TemplateDirective):
    help = (
        "Creates an Esmerald app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        app_name = options.pop("name")
        super().handle("app", app_name, **options)
