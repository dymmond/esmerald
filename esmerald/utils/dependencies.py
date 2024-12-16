import inspect
from typing import Any, Awaitable, Callable, Dict, Type, Union

from esmerald import params
from esmerald.security.scopes import Scopes
from esmerald.utils.helpers import is_async_callable, is_class_and_subclass


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


class RequiresDependency:
    def __init__(self):
        self._registry: Dict[Type, Union[Callable[..., Any], Awaitable]] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(
        self, dependency_type: Type, factory: Callable[..., Any], singleton: bool = False
    ):
        """
        Register a dependency with the injector.
        Args:
            dependency_type: The type to register.
            factory: A callable or coroutine function to create the dependency.
            singleton: Whether to cache the dependency instance.
        """
        self._registry[dependency_type] = (factory, singleton)

    async def resolve(self, dependency_type: Type) -> Any:
        """
        Resolve a dependency, supporting both Requires and normal dependencies.
        Args:
            dependency_type: The type to resolve.
        Returns:
            The resolved dependency instance.
        """

        if isinstance(dependency_type, params.Requires):
            return await self._resolve_requires(dependency_type)

        if dependency_type not in self._registry:
            raise ValueError(f"Dependency '{dependency_type.__name__}' is not registered.")

        factory, singleton = self._registry[dependency_type]

        if singleton and dependency_type in self._singletons:
            return self._singletons[dependency_type]

        instance = await self._execute_factory(factory)

        if singleton:
            self._singletons[dependency_type] = instance

        return instance

    async def _resolve_requires(self, requires: params.Requires) -> Any:
        """
        Resolve a Requires object by resolving its dependency.
        Args:
            requires: The Requires instance to resolve.
        Returns:
            The resolved dependency instance.
        """
        if requires.dependency is None:
            raise ValueError("Requires object must have a 'dependency' to resolve.")

        # Check if cached
        if requires.use_cache and requires.dependency in self._singletons:
            return self._singletons[requires.dependency]

        # Resolve the dependency
        resolved_dependency = await self.resolve(requires.dependency)

        # Cache if necessary
        if requires.use_cache:
            self._singletons[requires.dependency] = resolved_dependency

        return resolved_dependency

    async def _execute_factory(self, factory: Union[Callable[..., Any], Awaitable]) -> Any:
        """
        Execute a factory, handling async and sync functions.
        Args:
            factory: The factory to execute.
        Returns:
            The created dependency instance.
        """
        if is_async_callable(factory):
            return await factory()
        return factory()

    def dependency_tree(self) -> Dict[str, Any]:
        """
        Provide a tree view of registered dependencies.
        Returns:
            A dictionary representation of the dependency tree.
        """
        return {
            dependency.__name__: {
                "factory": factory.__name__ if callable(factory) else str(factory),
                "singleton": singleton,
            }
            for dependency, (factory, singleton) in self._registry.items()
        }


async def get_requires_dependency(
    injector: RequiresDependency, func: Callable, *args, **kwargs
) -> Any:
    """
    Recursively registers all dependencies required by a function.
    Args:
        injector: The dependency injector instance.
        func: The function to register dependencies for.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    Returns:
        The result of calling the function with all dependencies registered.
    """

    async def register_param(param: Any):
        if isinstance(param, params.Requires):
            # Register the dependency
            injector.register(
                param.dependency, lambda: param.dependency, singleton=param.use_cache
            )
            # Recursively register dependencies of the resolved dependency
            await get_requires_dependency(injector, param.dependency)
        return param

    # Inspect the function signature
    sig = inspect.signature(func)

    # Collect arguments to pass to the function
    registered_args = {}
    for param_name, param in sig.parameters.items():
        if param_name in kwargs:
            # Use the explicitly provided argument if given
            registered_args[param_name] = kwargs[param_name]
        elif isinstance(param.default, params.Requires):
            # Register dependencies specified as Requires
            registered_args[param_name] = await register_param(param.default)
        elif param.default is not inspect.Parameter.empty:
            # Use the default value if no Requires is specified
            registered_args[param_name] = param.default
        else:
            raise ValueError(
                f"Cannot register parameter '{param_name}' for function '{func.__name__}'."
            )
    # Call the function with registered arguments
    dependent =  await injector.resolve(func) if not registered_args else await injector.resolve(func(**registered_args))

    if is_async_callable(dependent):
        return await dependent()
    return dependent()
