from abc import ABC, abstractmethod
from typing import Any, Set

from lilya._internal._connection import Connection
from lilya.types import ASGIApp, Receive, Scope, Send
from typing_extensions import Annotated, Doc

from esmerald.enums import ScopeType
from esmerald.parsers import ArbitraryBaseModel
from esmerald.protocols.middleware import MiddlewareProtocol


class AuthResult(ArbitraryBaseModel):
    user: Annotated[
        Any,
        Doc(
            """
            Arbitrary user coming from the `authenticate` of the `BaseAuthMiddleware`
            and can be assigned to the `request.user`.
            """
        ),
    ]


class BaseAuthMiddleware(ABC, MiddlewareProtocol):  # pragma: no cover
    """
    `BaseAuthMiddleware` is the object that you can implement if you
    want to implement any `authentication` middleware with Esmerald.

    It is not mandatory to use it and you are free to implement your.

    Esmerald being based on Lilya, also offers a simple but powerful
    interface for handling `authentication` and [permissions](https://esmerald.dev/permissions/).

    Once you have installed the `AuthenticationMiddleware` and implemented the
    `authenticate`, the `request.user` will be available in any of your
    endpoints.

    Read more about how [Esmerald implements](https://esmerald.dev/middleware/middleware#baseauthmiddleware) the `BaseAuthMiddleware`.

    When implementing the `authenticate`, you must assign the result into the
    `AuthResult` object in order for the middleware to assign the `request.user`
    properly.

    The `AuthResult` is of type `esmerald.middleware.authentication.AuthResult`.
    """

    def __init__(
        self,
        app: Annotated[
            ASGIApp,
            Doc(
                """
                An ASGI type callable.
                """
            ),
        ],
    ):
        super().__init__(app)
        self.app = app
        self.scopes: Set[str] = {ScopeType.HTTP, ScopeType.WEBSOCKET}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Function callable that automatically will call the `authenticate` function
        from any middleware subclassing the `BaseAuthMiddleware` and assign the `AuthUser` user
        to the `request.user`.
        """
        if scope["type"] not in self.scopes:
            await self.app(scope, receive, send)
            return

        auth_result = await self.authenticate(Connection(scope))
        scope["user"] = auth_result.user
        await self.app(scope, receive, send)

    @abstractmethod
    async def authenticate(self, request: Connection) -> AuthResult:
        """
        The abstract method that needs to be implemented for any authentication middleware.
        """
        raise NotImplementedError("authenticate must be implemented.")
