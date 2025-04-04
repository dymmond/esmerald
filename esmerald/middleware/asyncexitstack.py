import traceback
from contextlib import AsyncExitStack
from typing import Optional

from lilya.types import ASGIApp, Receive, Scope, Send

from esmerald.core.config import AsyncExitConfig
from esmerald.protocols.middleware import MiddlewareProtocol


class AsyncExitStackMiddleware(MiddlewareProtocol):
    def __init__(
        self,
        app: "ASGIApp",
        config: "AsyncExitConfig",
        debug: bool = False,
    ):
        """AsyncExitStack Middleware class.

        Args:
            app: The 'next' ASGI app to call.
            config: The AsyncExitConfig instance.
            debug: If the application should print the stack trace on any error.
        """
        super().__init__(app)
        self.app = app
        self.config = config
        self.debug = debug

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if not AsyncExitStack:
            await self.app(scope, receive, send)  # pragma: no cover

        exception: Optional[Exception] = None
        async with AsyncExitStack() as stack:
            scope[self.config.context_name] = stack
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                exception = e

        if exception and self.debug:
            traceback.print_exception(exception, exception, exception.__traceback__)  # type: ignore

        if exception:
            raise exception
