from typing import Any

from lilya.types import ASGIApp, Receive, Scope, Send
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class MiddlewareProtocol(Protocol):  # pragma: no cover
    def __init__(self, app: "ASGIApp", **kwargs: Any): ...

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None: ...
