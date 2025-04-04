"""
Functions to use with the Factory dependency injection.
"""

from importlib import import_module
from typing import Any, Callable, Tuple, cast

from lilya._internal._module_loading import import_string  # noqa

from esmerald.exceptions import ImproperlyConfigured


def _resolve_imported_attribute(target: str, attribute: str) -> Any:  # pragma: no cover
    """
    Dynamically imports a module and retrieves the requested attribute.

    This function efficiently resolves deeply nested attributes by progressively importing
    each module level while avoiding redundant re-imports.

    Args:
        target (str): The fully qualified module path (e.g., "module.something").
        attribute (str): The attribute name to retrieve from the module.

    Returns:
        Any: The resolved attribute.

    Raises:
        ImportError: If the module or attribute cannot be imported.
    """
    try:
        module = import_module(target)
        return getattr(module, attribute)
    except ModuleNotFoundError:
        # If `target` is not a module, progressively resolve attributes.
        components = target.split(".")
        module_name = components.pop(0)
        module = __import__(module_name)

        for comp in components:
            module_name += f".{comp}"
            try:
                module = getattr(module, comp)
            except AttributeError:
                module = import_module(module_name)

        return getattr(module, attribute)
    except AttributeError as e:
        raise ImportError(f"Module '{target}' has no attribute '{attribute}'.") from e


def _get_provider_callable(provider: str) -> Callable[[], Any]:  # pragma: no cover
    """
    Returns a lazy loader function for a given provider string.

    Args:
        provider (str): The fully qualified import path (e.g., "myapp.daos.MyDAO").

    Returns:
        Callable[[], Any]: A function that, when called, imports and returns the attribute.

    Raises:
        TypeError: If the provider string is not in the correct format.
    """
    try:
        target, attribute = provider.rsplit(".", 1)
    except (ValueError, AttributeError, TypeError):
        raise TypeError(
            f"Invalid provider format: {provider!r}. Expected 'module.attribute'."
        ) from None

    return lambda: _resolve_imported_attribute(target, attribute)


def load_provider(provider: str) -> Tuple[Callable, bool]:  # pragma: no cover
    """
    Dynamically loads a callable provider from a string reference.

    This function allows for dependency injection without explicit imports,
    enabling modular and scalable application architecture.

    Args:
        provider (str): The fully qualified import path (e.g., "myapp.daos.MyDAO").

    Returns:
        Tuple[Callable, bool]: A tuple containing:
            - The resolved callable provider.
            - A boolean indicating if the provider was lazily loaded (nested import).

    Raises:
        ImproperlyConfigured: If the provider is not a string.
        ImproperlyConfigured: If the resolved object is not callable.
    """
    if not isinstance(provider, str):
        raise ImproperlyConfigured(
            "The `provider` must be a string with the format '<module>.<callable>'."
        )

    is_nested: bool = False
    provider_callable: Callable

    try:
        provider_callable = import_string(provider)
    except ModuleNotFoundError:
        provider_callable = _get_provider_callable(provider)
        is_nested = True

    if not callable(provider_callable):
        raise ImproperlyConfigured(
            f"The `provider` must be callable, but `{provider}` is of type `{type(provider_callable)}`."
        )

    return cast(Callable, provider_callable), is_nested
