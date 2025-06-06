ESMERALD_DISCOVER_APP = "ESMERALD_DEFAULT_APP"
DEFAULT_TEMPLATE_NAME = "default"
APP_PARAMETER = "--app"
HELP_PARAMETER = "--help"
EXCLUDED_DIRECTIVES = ["createproject", "createapp", "createdeployment"]
IGNORE_DIRECTIVES = ["directives"]
DISCOVERY_FILES = ["application.py", "app.py", "main.py", "asgi.py"]
DISCOVERY_FUNCTIONS = ["get_application", "get_app"]
DISCOVERY_ATTRS = ["application", "app"]
TREAT_AS_PROJECT_DIRECTIVE = ["deployment"]
