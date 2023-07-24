from abc import ABC, abstractmethod
from typing import Any

from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Receive, Scope, Send

from esmerald.enums import ScopeType
from esmerald.parsers import ArbitraryBaseModel
from esmerald.protocols.middleware import MiddlewareProtocol


class AuthResult(ArbitraryBaseModel):
    user: Any


class BaseAuthMiddleware(ABC, MiddlewareProtocol):  # pragma: no cover
    scopes = {ScopeType.HTTP, ScopeType.WEBSOCKET}

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        auth_result = await self.authenticate(HTTPConnection(scope))
        scope["user"] = auth_result.user
        await self.app(scope, receive, send)

    @abstractmethod
    async def authenticate(self, request: HTTPConnection) -> AuthResult:
        """
        The abstract method that needs to be implemented for any authentication middleware.
        """
        raise NotImplementedError("authenticate must be implemented.")
