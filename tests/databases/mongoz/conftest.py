import asyncio
import typing

import pytest

from esmerald import settings

client = settings.mongoz_registry


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": False})


@pytest.fixture(scope="session")
def event_loop() -> typing.Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def test_database() -> typing.AsyncGenerator:
    await client.drop_database("test_db")
    yield
    await client.drop_database("test_db")
