from typing import TYPE_CHECKING, Any

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from esmerald.types import ASGIApp, Receive, Scope, Send


@runtime_checkable
class ExtensionProtocol(Protocol):  # pragma: no cover
    def __init__(self, app: "ASGIApp", **kwargs: Any):
        ...

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        ...

    async def plug(self, app: "ASGIApp", kwargs: Any) -> None:
        ...
