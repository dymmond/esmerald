from typing import Any, Dict, Optional

from lilya.types import ASGIApp
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class ExtensionProtocol(Protocol):  # pragma: no cover
    def __init__(self, app: Optional["ASGIApp"] = None, **kwargs: Dict[Any, Any]): ...

    def extend(self, **kwargs: Any) -> None: ...
