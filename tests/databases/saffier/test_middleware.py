import random
import string
import time as pytime
from datetime import datetime, timedelta
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald, Gateway, Request, get
from esmerald.conf import settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.saffier.base_user import AbstractUser
from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
from esmerald.security.jwt.token import Token
from esmerald.testclient import create_client

database, models = settings.registry
pytestmark = pytest.mark.anyio


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


class User(AbstractUser):
    """
    Inherits from the abstract user and adds the registry
    from esmerald settings.
    """

    class Meta:
        registry = models


jwt_config = JWTConfig(signing_key=settings.secret_key)


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    await models.create_all()
    yield
    await models.drop_all()


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with database.force_rollback():
        async with database:
            yield


def generate_user_token(user: User, time=None):
    """
    Generates a user token
    """
    if not time:
        later = datetime.now() + timedelta(minutes=20)
    else:
        later = time

    token = Token(sub=user.id, exp=later)
    return token.encode(key=jwt_config.signing_key, algorithm=jwt_config.algorithm)


async def get_user_and_token(time=None):
    user = await User.query.create_user(
        first_name="Test",
        last_name="test",
        email="foo@bar.com",
        password="1234password",
        username="test",
    )

    token = generate_user_token(user, time=time)
    return token


@get()
async def home(request: Request) -> dict:
    return {"message": f"hello {request.user.email}"}


@pytest.fixture()
def app():
    app = Esmerald(
        routes=[Gateway(handler=home)],
        middleware=[StarletteMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
    )
    return app


@pytest.fixture()
async def async_client(app) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


async def test_cannot_access_endpoint_without_header(test_client_factory):
    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[StarletteMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
    ) as client:
        response = client.get("/")

        assert response.status_code == 401


async def test_cannot_access_endpoint_with_invalid_header(test_client_factory):
    time = datetime.now() + timedelta(seconds=1)
    token = await get_user_and_token(time=time)

    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[StarletteMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
    ) as client:
        response = client.get("/", headers={jwt_config.api_key_header: token})

        assert response.status_code == 401


async def test_cannot_access_endpoint_with_invalid_token(test_client_factory):
    time = datetime.now() + timedelta(seconds=1)
    token = await get_user_and_token(time=time)

    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[StarletteMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
        raise_server_exceptions=False,
    ) as client:
        pytime.sleep(2)
        response = client.get("/", headers={jwt_config.api_key_header: f"Bearer {token}"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Signature has expired."


async def test_can_access_endpoint_with_valid_token(test_client_factory, async_client):
    time = datetime.now() + timedelta(minutes=20)
    token = await get_user_and_token(time=time)

    response = await async_client.get("/", headers={jwt_config.api_key_header: f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"message": "hello foo@bar.com"}
