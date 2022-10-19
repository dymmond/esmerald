from typing import Optional

from esmerald.concurrency import AsyncExitStack
from esmerald.config import AsyncExitConfig
from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.types import ASGIApp, Receive, Scope, Send


class AsyncExitStackMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", config: "AsyncExitConfig"):
        """AsyncExitStack Middleware class.

        Args:
            app: The 'next' ASGI app to call.
            config: The AsyncExitConfig instance.
        """
        super().__init__(app)
        self.app = app
        self.config = config

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if not AsyncExitStack:
            await self.app(scope, receive, send)

        exception: Optional[Exception] = None
        async with AsyncExitStack() as stack:
            scope[self.config.context_name] = stack
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                exception = e
                raise e
            if exception:
                raise exception
