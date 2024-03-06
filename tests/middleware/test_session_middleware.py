import os
import re

import pytest
from lilya.responses import JSONResponse
from pydantic import ValidationError

from esmerald.config import SessionConfig
from esmerald.datastructures import Secret
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get, post
from esmerald.testclient import create_client
from esmerald.utils.crypto import get_random_secret_key


@pytest.mark.parametrize(
    "secret, should_raise",
    [
        [os.urandom(16), False],
        [os.urandom(24), False],
        [os.urandom(32), False],
        [os.urandom(17), True],
        [os.urandom(4), True],
        [os.urandom(100), True],
        [b"", True],
    ],
)
def test_config_validation(secret: bytes, should_raise: bool) -> None:
    if should_raise:
        with pytest.raises(ValidationError):
            SessionConfig(secret_key=Secret(secret))
    else:
        SessionConfig(secret_key=Secret(secret))


@get(path="/")
def view_session(request: Request) -> JSONResponse:
    return JSONResponse({"session": request.session})


@post(path="/")
async def update_session(request: Request) -> JSONResponse:
    data = await request.json()
    request.session.update(data)
    return JSONResponse({"session": request.session})


@post(path="/")
async def clear_session(request: Request) -> JSONResponse:
    request.session.clear()
    return JSONResponse({"session": request.session})


def test_session(test_client_factory):
    session_config = SessionConfig(secret_key=get_random_secret_key(32))
    with create_client(
        routes=[
            Gateway(path="/view_session", handler=view_session),
            Gateway(path="/update_session", handler=update_session),
            Gateway(path="/clear_session", handler=clear_session),
        ],
        session_config=session_config,
    ) as client:
        response = client.get("/view_session")
        assert response.json() == {"session": {}}

        response = client.post("/update_session", json={"some": "data"})
        assert response.json() == {"session": {"some": "data"}}

        # check cookie max-age
        set_cookie = response.headers["set-cookie"]
        max_age_matches = re.search(r"; Max-Age=([0-9]+);", set_cookie)
        assert max_age_matches is not None
        assert int(max_age_matches[1]) == 180 * 24 * 3600

        response = client.get("/view_session")
        assert response.json() == {"session": {"some": "data"}}

        response = client.post("/clear_session")
        assert response.json() == {"session": {}}

        response = client.get("/view_session")
        assert response.json() == {"session": {}}


def test_session_expires():
    session_config = SessionConfig(secret_key=get_random_secret_key(32), max_age=-1)

    with create_client(
        routes=[
            Gateway(path="/view_session", handler=view_session),
            Gateway(path="/update_session", handler=update_session),
        ],
        session_config=session_config,
    ) as client:
        response = client.post("/update_session", json={"some": "data"})
        assert response.json() == {"session": {"some": "data"}}

        expired_cookie_header = response.headers["set-cookie"]
        expired_session_match = re.search(r"session=([^;]*);", expired_cookie_header)

        assert expired_session_match is not None

        expired_session_value = expired_session_match[1]
        response = client.get("/view_session", cookies={"session": expired_session_value})
        assert response.json() == {"session": {}}
