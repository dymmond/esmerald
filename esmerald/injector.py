from typing import TYPE_CHECKING, Any, Dict, Optional, Type, cast

from esmerald.transformers.datastructures import Signature as SignatureModel
from esmerald.typing import Void
from esmerald.utils.helpers import is_async_callable
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.typing import AnyCallable, DictAny


class Inject(BaseModel):
    dependency: Optional["AnyCallable"]
    use_cache: Optional[bool]
    value: Optional[Any]
    signature_model: Optional["Type[SignatureModel]"]

    def __init__(self, dependency: "AnyCallable", use_cache: bool = False, **kwargs: "DictAny"):
        super().__init__(**kwargs)
        self.dependency = cast("AnyCallable", dependency)
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
