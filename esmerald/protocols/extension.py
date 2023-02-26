from typing import TYPE_CHECKING, Any, Dict, Optional

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from esmerald.types import ASGIApp


@runtime_checkable
class ExtensionProtocol(Protocol):  # pragma: no cover
    def __init__(self, app: Optional["ASGIApp"] = None, **kwargs: Dict[Any, Any]):
        ...

    def extend(self, **kwargs: Any) -> None:
        ...
