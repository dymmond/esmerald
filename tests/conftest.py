import functools
import pathlib
from typing import Any, List

import pytest

from esmerald import AsyncDAOProtocol
from esmerald.encoders import MsgSpecEncoder, PydanticEncoder, register_esmerald_encoder
from esmerald.testclient import EsmeraldTestClient

register_esmerald_encoder(PydanticEncoder)
register_esmerald_encoder(MsgSpecEncoder)


class FakeDAO(AsyncDAOProtocol):
    model = "Awesome"

    def __init__(self, conn: str = "awesome_conn"):
        self.conn = conn

    async def get_all(self, **kwargs: Any) -> List[Any]:
        return ["awesome_data"]


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
