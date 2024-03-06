"""
Functions to use with the Factory dependency injection.
"""

from typing import Any, Callable, Tuple, cast

from lilya._internal._module_loading import import_string

from esmerald.exceptions import ImproperlyConfigured


def _lookup(klass: Any, comp: Any, import_path: Any) -> Any:  # pragma: no cover
    """
    Runs a lookup via __import__ and returns the component.
    """
    try:
        return getattr(klass, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(klass, comp)


def _importer(target: Any, attribute: Any) -> Any:  # pragma: no cover
    """
    Gets the attribute from the target.
    """
    components = target.split(".")
    import_path = components.pop(0)
    klass = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        klass = _lookup(klass, comp, import_path)
    return getattr(klass, attribute)


def _get_provider_callable(target: str) -> Any:  # pragma: no cover
    try:
        target, attribute = target.rsplit(".", 1)
    except (TypeError, ValueError, AttributeError):
        raise TypeError(f"Need a valid target to lookup. You supplied: {target!r}") from None

    def getter() -> Any:
        return _importer(target, attribute)

    return getter


def load_provider(provider: str) -> Tuple[Callable, bool]:  # pragma: no cover
    """
    Loads any callable by string import. This will make
    sure that there is no need to have all the imports in one
    file to use the `esmerald.injector.Factory`.

    Example:
        # myapp.daos.py
        from esmerald import AsyncDAOProtocol


        class MyDAO(AsyncDAOProtocol):
            ...

        # myapp.urls.py
        from esmerald import Inject, Factory, Gateway

        route_patterns = [
            Gateway(
                ...,
                dependencies={"my_dao": Inject(Factory("myapp.daos.MyDAO"))}
            )
        ]
    """
    if not isinstance(provider, str):
        raise ImproperlyConfigured(
            "The `provider` should be a string with the format <module>.<file>"
        )

    is_nested: bool = False
    try:
        provider_callable = import_string(provider)
    except ModuleNotFoundError:
        target = _get_provider_callable(provider)
        provider_callable = target
        is_nested = True

    if not callable(provider_callable):
        raise ImproperlyConfigured(
            f"The `provider` specified must be a callable, got {type(provider_callable)} instead."
        )

    return cast(Callable, provider_callable), is_nested
