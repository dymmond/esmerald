import pytest

from esmerald.injector import Factory


# Sample classes and functions for testing
class SampleClass:
    def __init__(self, x: int, y: int = 0) -> None:
        self.x = x
        self.y = y

    def sum(self) -> int:
        return self.x + self.y


async def async_function(a: int, b: int) -> int:
    return a + b


def sync_function(a: int, b: int) -> int:
    return a + b


@pytest.mark.asyncio
async def test_factory_with_args():
    """Ensure Factory correctly passes positional arguments."""
    factory = Factory(SampleClass, 5, 10)
    instance = await factory()
    assert isinstance(instance, SampleClass)
    assert instance.sum() == 15  # 5 + 10


@pytest.mark.asyncio
async def test_factory_with_kwargs():
    """Ensure Factory correctly passes keyword arguments."""
    factory = Factory(SampleClass, x=3, y=7)
    instance = await factory()
    assert isinstance(instance, SampleClass)
    assert instance.sum() == 10  # 3 + 7


@pytest.mark.asyncio
async def test_factory_with_args_and_kwargs():
    """Ensure Factory handles both positional and keyword arguments."""
    factory = Factory(SampleClass, 2, y=8)
    instance = await factory()
    assert isinstance(instance, SampleClass)
    assert instance.sum() == 10  # 2 + 8


@pytest.mark.asyncio
async def test_factory_with_sync_function():
    """Ensure Factory works with normal sync functions."""
    factory = Factory(sync_function, 4, 6)
    result = await factory()
    assert result == 10  # 4 + 6


@pytest.mark.asyncio
async def test_factory_with_async_function():
    """Ensure Factory supports async callables."""
    factory = Factory(async_function, 3, 9)
    result = await factory()
    assert result == 12  # 3 + 9


@pytest.mark.asyncio
async def test_factory_with_string_import():
    """Ensure Factory works with string-based imports (nested classes)."""
    factory = Factory("tests.test_factory.SampleClass", 1, 2)
    instance = await factory()
    assert isinstance(instance, SampleClass)
    assert instance.sum() == 3  # 1 + 2
