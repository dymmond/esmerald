import functools
from functools import partial
from typing import Any, Awaitable, Callable, Generic, List, TypeVar, Union

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
            self.fn = partial(run_sync, fn)  # type:ignore[assignment]

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.fn(*args, **kwargs)


def as_async_callable_list(value: Union[Callable, List[Callable]]) -> List[AsyncCallable]:
    if not isinstance(value, list):
        return [AsyncCallable(value)]
    return [AsyncCallable(v) for v in value]


def execsync(async_function: Any, raise_error: bool = True):
    """
    Runs any async function inside a blocking function (sync).
    """

    @functools.wraps(async_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_async_module = getattr(threadlocals, "current_async_module", None)
        partial_func = functools.partial(async_function, *args, **kwargs)
        if current_async_module is not None and raise_error is True:
            return anyio.from_thread.run(partial_func)
        return anyio.run(partial_func)

    return wrapper
