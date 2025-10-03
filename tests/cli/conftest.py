import asyncio
from typing import Generator

import pytest
from sayer.testing import SayerTestClient

from ravyn.core.directives.cli import ravyn_cli


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": True})


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Fixture to provide a test client for the Lilya CLI."""
    return SayerTestClient(ravyn_cli)
