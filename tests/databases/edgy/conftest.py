import asyncio
from typing import Generator

import pytest


def pytest_configure(config):
    config.option.asyncio_mode = "strict"


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": True})


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
