from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

from esmerald.core.di.provider import load_provider
from esmerald.parsers import ArbitraryHashableBaseModel
from esmerald.transformers.datastructures import Signature
from esmerald.typing import Void
from esmerald.utils.helpers import is_async_callable

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.typing import AnyCallable


class Factory:
    def __init__(self, provides: Union["AnyCallable", str], *args: Any) -> None:
        """
        The provider can be passed in separate ways. Via direct callable
        or via string value where it will be automatically imported by the application.
        """
        self.__args: Tuple[Any, ...] = ()
        self.set_args(*args)
        self.is_nested: bool = False

        if isinstance(provides, str):
            self.provides, self.is_nested = load_provider(provides)
        else:
            self.provides = provides

    def set_args(self, *args: Any) -> None:
        self.__args = args

    @property
    def cls(self) -> "AnyCallable":  # pragma: no cover
        """Return provided type."""
        return self.provides

    async def __call__(self) -> Any:
        """
        This handles with normal and nested imports.

        Example:

            1. MyClass.func
            2. MyClass.AnotherClass.func
        """
        if self.is_nested:
            self.provides = self.provides()

        if is_async_callable(self.provides):
            value = await self.provides(*self.__args)
        else:
            value = self.provides(*self.__args)
        return value


class Inject(ArbitraryHashableBaseModel):
    def __init__(self, dependency: "AnyCallable", use_cache: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.dependency = dependency
        self.signature_model: Optional["Type[Signature]"] = None
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
