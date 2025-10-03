from typing import Any, Dict

from ravyn.core.protocols.middleware import MiddlewareProtocol
from ravyn.types import ASGIApp, Receive, Scope, Send


class SampleMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", **kwargs):
        """SampleMiddleware Middleware class.

        The `app` is always enforced.

        Args:
            app: The 'next' ASGI app to call.
            kwargs: Any arbitrarty data.
        """
        super().__init__(app)
        self.app = app
        self.kwargs = kwargs

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Implement the middleware logic here
        """
        ...


class AnotherSample(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", **kwargs: Dict[str, Any]):
        super().__init__(app, **kwargs)
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        await self.app(scope, receive, send)
