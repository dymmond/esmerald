import asyncio
import functools
import pathlib
import typing
from typing import Any, List

import pytest
from mongoz.core.connection.registry import Registry

from esmerald import AsyncDAOProtocol
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TEST_DATABASE_URL

database_uri = TEST_DATABASE_URL
client = Registry(database_uri, event_loop=asyncio.get_running_loop)


class FakeDAO(AsyncDAOProtocol):
    model = "Awesome"

    def __init__(self, conn: str = "awesome_conn"):
        self.conn = conn

    async def get_all(self, **kwargs: Any) -> List[Any]:
        return ["awesome_data"]


@pytest.fixture
def no_trio_support(anyio_backend_name):  # pragma: no cover
    if anyio_backend_name == "trio":
        pytest.skip("Trio not supported (yet!)")


@pytest.fixture
def test_client_factory(anyio_backend_name, anyio_backend_options):
    # anyio_backend_name defined by:
    # https://anyio.readthedocs.io/en/stable/testing.html#specifying-the-backends-to-run-on
    return functools.partial(
        EsmeraldTestClient,
        backend=anyio_backend_name,
        backend_options=anyio_backend_options,
    )


@pytest.fixture
def test_app_client_factory(anyio_backend_name, anyio_backend_options):
    # anyio_backend_name defined by:
    # https://anyio.readthedocs.io/en/stable/testing.html#specifying-the-backends-to-run-on
    return functools.partial(
        EsmeraldTestClient,
        backend=anyio_backend_name,
        backend_options=anyio_backend_options,
    )


@pytest.fixture()
def template_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path


@pytest.fixture(scope="module")
def get_fake_dao():
    return FakeDAO


@pytest.fixture(scope="module")
def get_fake_dao_instance():
    return FakeDAO()


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
