import inspect
from typing import Any, Dict, Union

from lilya.compat import run_sync
from lilya.context import request_context

from esmerald import params
from esmerald.security.scopes import Scopes
from esmerald.utils.helpers import is_class_and_subclass


def is_requires_scheme(param: Any) -> bool:
    """
    Checks if the object is a security scheme.
    """
    return is_class_and_subclass(param, params.Requires)


def is_security_scheme(param: Any) -> bool:
    """
    Checks if the object is a security scheme.
    """
    if not param:
        return False
    return isinstance(param, params.Security)


def is_base_requires(param: Any) -> bool:
    """
    Checks if the object is a base requires object.
    """
    return is_class_and_subclass(param, params.BaseRequires)


def is_security_scope(param: Any) -> bool:
    """
    Checks if the object is a security scope object.
    """
    if not param:
        return False
    return is_class_and_subclass(param, Scopes)


def is_inject(param: Any) -> bool:
    """
    Checks if the object is an Inject.
    """
    from esmerald.injector import Inject

    return isinstance(param, Inject)


def is_requires(param: Any) -> bool:
    """
    Checks if the object is an Inject.
    """
    if not param:
        return False
    return isinstance(param, params.Requires)


async def async_resolve_dependencies(func: Any, overrides: Union[Dict[str, Any]] = None) -> Any:
    """
    Resolves dependencies for an asynchronous function by inspecting its signature and
    recursively resolving any dependencies specified using the `params.Requires` class.
    Args:
        func (Any): The target function whose dependencies need to be resolved.
        overrides (Union[Dict[str, Any]], optional): A dictionary of overrides for dependencies.
            This can be used for testing or customization. Defaults to None.
    Returns:
        Any: The result of the target function with its dependencies resolved.
    Raises:
        TypeError: If the target function or any of its dependencies are not callable.
    """
    if overrides is None:
        overrides = {}

    signature = inspect.signature(func)
    kwargs = {}

    for name, param in signature.parameters.items():
        # If in one of the requirements happens to be Security, we need to resolve it
        # By passing the Request object to the dependency
        if isinstance(param.default, params.Security):
            kwargs[name] = await param.default.dependency(request_context)
        if isinstance(param.default, params.Requires):
            dep_func = param.default.dependency
            dep_func = overrides.get(dep_func, dep_func)  # type: ignore
            if inspect.iscoroutinefunction(dep_func):
                resolved = await async_resolve_dependencies(dep_func, overrides)
            else:
                resolved = (
                    resolve_dependencies(dep_func, overrides) if callable(dep_func) else dep_func
                )
            kwargs[name] = resolved
    if inspect.iscoroutinefunction(func):
        return await func(**kwargs)
    else:
        return func(**kwargs)


def resolve_dependencies(func: Any, overrides: Union[Dict[str, Any]] = None) -> Any:
    """
    Resolves the dependencies for a given function.

    Parameters:
        func (Any): The function for which dependencies need to be resolved.
        overrides (Union[Dict[str, Any], None], optional): A dictionary of dependency overrides. Defaults to None.
        Raises:
        ValueError: If the provided function is asynchronous.

    Returns:
        Any: The result of running the asynchronous dependency resolution function.
    """
    if overrides is None:
        overrides = {}
    if inspect.iscoroutinefunction(func):
        raise ValueError("Function is async. Use resolve_dependencies_async instead.")
    return run_sync(async_resolve_dependencies(func, overrides))
