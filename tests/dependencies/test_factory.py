from typing import Any

import pytest

from esmerald import Factory, Gateway, JSONResponse, get
from esmerald.protocols.asyncdao import AsyncDAOProtocol
from esmerald.testclient import create_client


class AnotherFakeDAO(AsyncDAOProtocol):
    model = "Awesome"

    def __init__(self, value: str = "awesome_conn", **kwargs: Any):
        self.value = value
        self.kwargs = kwargs

    async def get_all(self, **kwargs: Any):
        return ["awesome_data"]

    async def get_kwargs(self):
        return self.kwargs


@get(
    "/test",
    dependencies={
        "dao": Factory(AnotherFakeDAO, "awesome_conn", db_session="session", cache="cache")
    },
)
async def test_view(dao: AnotherFakeDAO) -> JSONResponse:
    res = await dao.get_kwargs()
    return JSONResponse(res)


def test_kwargs_in_factory():
    """Ensure Factory correctly passes keyword arguments."""

    with create_client(routes=[Gateway(handler=test_view)]) as client:
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"db_session": "session", "cache": "cache"}


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
    factory = Factory("tests.dependencies.test_factory.SampleClass", 1, 2)
    instance = await factory()
    assert isinstance(instance, SampleClass)
    assert instance.sum() == 3  # 1 + 2
