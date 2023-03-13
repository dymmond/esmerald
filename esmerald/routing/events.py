from typing import TYPE_CHECKING, List, Optional, TypeVar

from starlette._utils import is_async_callable
from starlette.types import Receive, Scope, Send

if TYPE_CHECKING:
    from esmerald.types import DictAny, LifeSpanHandler


_T = TypeVar("_T")


class AyncLifespanContextManager:
    """
    Manages and handles the on_startup and on_shutdown events
    in an Esmerald way.

    This is not the same as the on_startup and on_shutdown
    from Starlette. Those are now deprecated and will be removed
    in the version 1.0 of Starlette.

    This aims to provide a similar functionality but by generating
    a lifespan event based on the values from the on_startup and on_shutdown
    lists.
    """

    def __init__(
        self,
        on_shutdown: Optional[List["LifeSpanHandler"]] = None,
        on_startup: Optional[List["LifeSpanHandler"]] = None,
    ) -> None:
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)

    def __call__(self: _T, app: object) -> _T:
        return self

    async def __aenter__(self):
        """Runs the functions on startup"""
        for handler in self.on_startup:
            if is_async_callable(handler):
                await handler()
            else:
                handler()

    async def __aexit__(self, scope: Scope, receive: Receive, send: Send, **kwargs: "DictAny"):
        """Runs the functions on shutdown"""
        for handler in self.on_shutdown:
            if is_async_callable(handler):
                await handler()
            else:
                handler()
