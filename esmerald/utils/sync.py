import functools
from functools import partial
from typing import Any, Awaitable, Callable, Generic, TypeVar

import anyio
from anyio._core._eventloop import threadlocals
from anyio.to_thread import run_sync
from typing_extensions import ParamSpec

from esmerald.utils.helpers import is_async_callable

P = ParamSpec("P")
T = TypeVar("T")


class AsyncCallable(Generic[P, T]):
    __slots__ = ("args", "kwargs", "fn")

    def __init__(self, fn: Callable[P, T]):
        self.fn: Callable[P, Awaitable[T]]
        if is_async_callable(fn):
            self.fn = fn
        else:
            self.fn = partial(run_sync, fn)

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.fn(*args, **kwargs)


def execsync(async_function: Callable[..., T], raise_error: bool = True) -> Callable[..., T]:
    """
    Runs any async function inside a blocking function (sync).
    """

    @functools.wraps(async_function)
    def wrapper(*args: Any, **kwargs: Any) -> T:  # pragma: no cover
        current_async_module = getattr(threadlocals, "current_async_module", None)
        partial_func = functools.partial(async_function, *args, **kwargs)
        if current_async_module is not None and raise_error is True:
            return anyio.from_thread.run(partial_func)  # type: ignore
        return anyio.run(partial_func)  # type: ignore

    return wrapper
