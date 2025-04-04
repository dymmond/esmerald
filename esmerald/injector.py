from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

from esmerald.core.injector.provider import load_provider
from esmerald.core.transformers.signature import SignatureModel
from esmerald.parsers import ArbitraryHashableBaseModel
from esmerald.typing import Void
from esmerald.utils.helpers import is_async_callable

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.typing import AnyCallable


class Factory:
    def __init__(self, provides: Union["AnyCallable", str], *args: Any, **kwargs: Any) -> None:
        """
        A dependency injection factory that supports both positional and keyword arguments.

        The provider can be passed as either:
        - A direct callable
        - A string reference to be dynamically imported

        Example Usage:
            dependencies = {
                "user": Factory(UserDAO, db_session=session, cache=cache)
            }
        """
        self.__args: Tuple[Any, ...] = args
        self.__kwargs: Dict[str, Any] = kwargs
        self.is_nested: bool = False

        if isinstance(provides, str):
            self.provides, self.is_nested = load_provider(provides)
        else:
            self.provides = provides

    def set_args(self, *args: Any, **kwargs: Any) -> None:
        """Set or update arguments dynamically."""
        self.__args = args
        self.__kwargs = kwargs

    @property
    def cls(self) -> "AnyCallable":  # pragma: no cover
        """Return the provided class or function."""
        return self.provides

    async def __call__(self) -> Any:
        """
        Instantiates the provided class/function, handling both sync and async cases.

        Supports:
            - Nested imports (e.g., MyClass.func, MyClass.SubClass.func)
            - Both sync and async callables
            - Positional and keyword arguments

        Example:
            Factory(UserDAO, db_session=session)
        """
        if self.is_nested:
            self.provides = self.provides()

        if is_async_callable(self.provides):
            return await self.provides(*self.__args, **self.__kwargs)
        return self.provides(*self.__args, **self.__kwargs)


class Inject(ArbitraryHashableBaseModel):
    def __init__(self, dependency: "AnyCallable", use_cache: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.dependency = dependency
        self.signature_model: Optional["Type[SignatureModel]"] = None
        self.use_cache = use_cache
        self.value: Any = Void

    async def __call__(self, **kwargs: Dict[str, Any]) -> Any:
        if self.use_cache and self.value is not Void:
            return self.value

        if is_async_callable(self.dependency):
            value = await self.dependency(**kwargs)
        else:
            value = self.dependency(**kwargs)

        if self.use_cache:
            self.value = value

        return value

    def __eq__(self, other: Any) -> bool:
        return other is self or (
            isinstance(other, self.__class__)
            and other.dependency == self.dependency
            and other.use_cache == self.use_cache
            and other.value == self.value
        )

    def __hash__(self) -> int:
        values: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))
