import asyncio
from concurrent import futures
from concurrent.futures import Future
from functools import partial
from typing import Any, Awaitable, Callable, Generic, TypeVar

from anyio import to_thread
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
            self.fn = partial(to_thread.run_sync, fn)

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.fn(*args, **kwargs)


def run_sync(async_function: Awaitable) -> Any:
    """
    Runs the queries in sync mode
    """
    try:
        return asyncio.run(async_function)  # type: ignore
    except RuntimeError:
        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future: Future = executor.submit(asyncio.run, async_function)  # type: ignore
            return future.result()
