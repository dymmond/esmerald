from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type

from esmerald.parsers import ArbitraryHashableBaseModel
from esmerald.transformers.datastructures import Signature
from esmerald.typing import Void
from esmerald.utils.helpers import is_async_callable

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.typing import AnyCallable


class Factory:
    def __init__(self, provides: "AnyCallable", *args: Any) -> None:
        self.provides = provides
        self.__args: Tuple[Any, ...] = ()
        self.set_args(*args)

    def set_args(self, *args: Any) -> None:
        self.__args = args

    @property
    def cls(self) -> "AnyCallable":
        """Return provided type."""
        return self.provides

    async def __call__(self) -> Any:
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
