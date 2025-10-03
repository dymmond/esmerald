from typing import Any

from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class SchedulerProtocol(Protocol):  # pragma: no cover
    def __init__(self, **kwargs: Any): ...

    async def start(self, **kwargs: dict[str, Any]) -> None: ...

    async def shutdown(self, **kwargs: dict[str, Any]) -> None: ...
