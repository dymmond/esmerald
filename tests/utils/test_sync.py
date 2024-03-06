from esmerald.utils.helpers import is_async_callable
from esmerald.utils.sync import AsyncCallable


async def process() -> None:
    """async function"""


def another_process() -> None:
    """sync function"""


def test_async_callable_return_async():
    async_callable = AsyncCallable(process)

    assert is_async_callable(async_callable.fn)


def test_async_callable_transform():
    async_callable = AsyncCallable(another_process)

    assert is_async_callable(async_callable.fn)
