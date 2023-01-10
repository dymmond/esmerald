from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from starlette.requests import HTTPConnection

from esmerald.protocols.interceptor import InterceptorProtocol

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send


class EsmeraldInterceptor(ABC, InterceptorProtocol):
    """Base class for any Esmerald interceptor in the system."""

    def __init__(self, app: "ASGIApp") -> None:
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: "Scope", send: "Send", receive: "Receive") -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        await self.intercept(HTTPConnection(scope))
        await self.app(scope, receive, send)

    @abstractmethod
    async def intercept(self, request: HTTPConnection) -> None:
        raise NotImplementedError("intercept must be implemented")
