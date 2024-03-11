from typing import TYPE_CHECKING, Any, Optional, Sequence, TypeVar

from lilya.compat import is_async_callable
from lilya.types import Lifespan, Receive, Scope, Send

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.types import LifeSpanHandler


_T = TypeVar("_T")


class AyncLifespanContextManager:  # pragma: no cover
    """
    Manages and handles the on_startup and on_shutdown events
    in an Esmerald way.

    This aims to provide a similar functionality but by generating
    a lifespan event based on the values from the on_startup and on_shutdown
    lists.
    """

    def __init__(
        self,
        on_shutdown: Optional[Sequence["LifeSpanHandler"]] = None,
        on_startup: Optional[Sequence["LifeSpanHandler"]] = None,
    ) -> None:
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)

    def __call__(self: _T, app: object) -> _T:
        return self

    async def __aenter__(self) -> None:
        """Runs the functions on startup"""
        for handler in self.on_startup:
            if is_async_callable(handler):
                await handler()  # type: ignore
            else:
                handler()

    async def __aexit__(self, scope: Scope, receive: Receive, send: Send, **kwargs: "Any") -> None:
        """Runs the functions on shutdown"""
        for handler in self.on_shutdown:
            if is_async_callable(handler):
                await handler()  # type: ignore
            else:
                handler()


def handle_lifespan_events(
    on_startup: Optional[Sequence["LifeSpanHandler"]] = None,
    on_shutdown: Optional[Sequence["LifeSpanHandler"]] = None,
    lifespan: Optional[Lifespan[Any]] = None,
) -> Any:  # pragma: no cover
    """Handles with the lifespan events in the new Lilya format of lifespan.
    This adds a mask that keeps the old `on_startup` and `on_shutdown` events variable
    declaration for legacy and comprehension purposes and build the async context manager
    for the lifespan.
    """
    if on_startup or on_shutdown:
        return AyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
    elif lifespan:
        return lifespan
    return None


def generate_lifespan_events(
    on_startup: Optional[Sequence["LifeSpanHandler"]] = None,
    on_shutdown: Optional[Sequence["LifeSpanHandler"]] = None,
    lifespan: Optional[Lifespan[Any]] = None,
) -> Any:  # pragma: no cover
    if lifespan:
        return lifespan
    return AyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
