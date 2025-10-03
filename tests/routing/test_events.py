from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

import pytest
from pydantic import BaseModel

from ravyn import Gateway, Ravyn, get
from ravyn.testclient import EsmeraldTestClient


class State(BaseModel):
    app_startup: bool = False
    app_shutdown: bool = False


@pytest.fixture
def state() -> State:
    return State()


def test_app_lifespan_state(state: State) -> None:
    @asynccontextmanager
    async def lifespan(app: Ravyn) -> AsyncGenerator[None, None]:
        state.app_startup = True
        yield
        state.app_shutdown = True

    @get("/")
    def main() -> Dict[str, str]:
        return {"message": "Hello World"}

    app = Ravyn(routes=[Gateway(handler=main)], lifespan=lifespan)

    assert state.app_startup is False
    assert state.app_shutdown is False

    with EsmeraldTestClient(app) as client:
        assert state.app_startup is True
        assert state.app_shutdown is False
        response = client.get("/")
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Hello World"}

    assert state.app_startup is True
    assert state.app_shutdown is True
