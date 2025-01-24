import sys

from esmerald import Esmerald, Include


def build_path():
    """
    Builds the path of the project and project root.
    """  #
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        # in case of an application model with apps
        sys.path.append(os.path.join(SITE_ROOT, "apps"))


def disable_edgy_settings_load():
    os.environ["EDGY_SETTINGS_MODULE"] = ""


def get_application():
    """
    Encapsulating in methods can be useful for controlling the import order but is optional.
    """
    # first call build_path
    build_path()
    # this is optional, for rewiring edgy settings to esmerald settings
    disable_edgy_settings_load()  # disable any settings load
    # import edgy now
    from edgy import Instance, monkay
    from esmerald.conf import settings

    monkay.settings = lambda: settings.edgy_settings  # rewire
    monkay.evaluate_settings_once(ignore_import_errors=False)  # import manually

    # now the project is in the search path and we can import
    registry = settings.registry

    app = registry.asgi(
        Esmerald(
            routes=[Include(namespace="my_project.urls")],
        )
    )

    monkay.set_instance(Instance(registry=registry, app=app))
    return app


app = get_application()
