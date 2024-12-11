from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Union

from esmerald import params
from esmerald.utils.helpers import is_class_and_subclass

if TYPE_CHECKING:
    from esmerald.requests import Request
    from esmerald.types import Dependencies
    from esmerald.websockets import WebSocket


@dataclass
class Required:
    """
    This class is used to define the required dependencies.
    """

    dependency: Any


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


def is_inject(param: Any) -> bool:
    """
    Checks if the object is an Inject.
    """
    from esmerald.injector import Inject

    return isinstance(param, Inject)


async def get_requires_dependency(
    key: str,
    dependencies: "Dependencies",
    connection: Union["Request", "WebSocket", None] = None,
    **kwargs: Any,
) -> Any:
    """
    Simple function that will check dependents and sub dependents based on
    the type of dependency and extract the dependency.
    """
    resolved = {}

    async def resolve(func: Callable[..., Any]) -> Any:
        """Recursively resolve a function and its dependencies."""
        if func in resolved:
            return resolved[func]

        _dependencies = []

        # Get the function's dependencies
        for dep in dependencies.get(key, []):
            # Check and resolve each dependency
            _dependencies.append(resolve(dep))

        # Store the resolved dependencies in the resolved dictionary
        if is_inject(func):
            resolved[func] = await func.dependency(**kwargs)
        resolved[func] = _dependencies
        return _dependencies

    # Resolve all functions in the dictionary
    for func in dependencies:
        await resolve(func)

    return resolved

def get_dependency_tree(key: str, dependencies: Dict[Callable, List[params.Requires]]) -> Dict[str, Any]:
    """Recursively resolve dependencies for a set of functions."""
    resolved = {}  # Maps the final result of dependency to its corresponding key
    in_progress = set()  # Set to detect circular dependencies

    def resolve(func):
        """Recursively resolve a function and its dependencies."""
        if func in resolved:
            return resolved[func]

        if func in in_progress:
            raise ValueError(f"Circular dependency detected involving '{func.__name__}'")

        # Mark this function as being processed
        in_progress.add(func)

        dependencies_for_func = dependencies.get(func, [])
        resolved_dependencies = {}

        # Resolve each dependency for the current function
        for dep in dependencies_for_func:
            dep_key = key
            dep_func = dep.dependency

            # Resolve the dependency and store it by key
            resolved_dependencies[dep_key] = resolve(dep_func)

        # Now that all dependencies are resolved, store the result
        resolved[func] = resolved_dependencies

        # Remove this function from the current recursion stack
        in_progress.remove(func)

        return resolved_dependencies

    # Resolve all dependencies
    for func in dependencies:
        resolve(func)

    return resolved
    # _dependencies: Dict[str, Any] = None

    # if requires.dependency is None:
    #     raise RuntimeError("Requires dependency cannot be undefined.")

    # if is_inject(requires.dependency):
    #     _dependencies = requires.dependency.get_dependencies()
