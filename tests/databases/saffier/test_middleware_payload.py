import random
import string
from datetime import datetime, timedelta
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from anyio import from_thread, sleep, to_thread
from httpx import AsyncClient
from lilya.middleware import DefineMiddleware as LilyaMiddleware
from pydantic import BaseModel
from saffier.exceptions import DoesNotFound

from esmerald import Esmerald, Gateway, Include, JSONResponse, Request, get, post, status
from esmerald.conf import settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.saffier.base_user import AbstractUser
from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
from esmerald.security.jwt.token import Token
from esmerald.testclient import create_client

database, models = settings.registry
pytestmark = pytest.mark.anyio


def get_random_string(length=10):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def blocking_function():
    from_thread.run(sleep, 2)


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
    try:
        await models.create_all()
        yield
        await models.drop_all()
    except Exception:
        pytest.skip("No database available")


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
    uuid = str(uuid4())[:6]
    user = await User.query.create_user(
        first_name="Test",
        last_name="test",
        email=f"{uuid}-foo@bar.com",
        password=get_random_string(),
        username=f"{uuid}-test",
    )

    token = generate_user_token(user, time=time)
    return token


class BackendAuthentication(BaseModel):
    email: str
    password: str

    async def authenticate(self) -> str:
        """Authenticates a user and returns a JWT string"""
        try:
            user: User = await User.query.get(email=self.email)
        except DoesNotFound:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            await User().set_password(self.password)
        else:
            is_password_valid = await user.check_password(self.password)
            if is_password_valid and self.user_can_authenticate(user):
                # Using the access_token_lifetime from the JWT config directly
                time = datetime.now() + jwt_config.access_token_lifetime
                return self.generate_user_token(user, time=time)

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)

    def generate_user_token(self, user: User, time=None):
        """
        Generates a user token
        """
        if not time:
            later = datetime.now() + timedelta(minutes=20)
        else:
            later = time

        token = Token(sub=user.id, exp=later)
        return token.encode(key=jwt_config.signing_key, algorithm=jwt_config.algorithm)


class UserIn(BaseModel):
    email: str
    password: str


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    username: str


@get()
async def home(request: Request) -> dict:
    return {"message": f"hello {request.user.email}"}


@post(status_code=status.HTTP_200_OK)
async def login(payload: UserIn, request: Request) -> JSONResponse:
    """
    Login a user and returns a JWT token, else raises ValueError
    """
    auth = BackendAuthentication(email=payload.email, password=payload.password)
    token = await auth.authenticate()
    return JSONResponse({jwt_config.access_token_name: token})


_string_pass = get_random_string()


@post()
async def create_user(payload: CreateUser) -> None:
    await User.query.create_user(
        first_name="Test",
        last_name="test",
        email="foo@bar.com",
        password=_string_pass,
        username="test",
    )


@pytest.fixture()
def app():
    app = Esmerald(
        routes=[
            Gateway("/login", handler=login),
            Gateway("/create", handler=create_user),
            Include(
                routes=[Gateway(handler=home)],
                middleware=[
                    LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)
                ],
            ),
        ],
    )
    return app


@pytest.fixture()
async def async_client(app) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await to_thread.run_sync(blocking_function)
        yield ac


async def test_cannot_access_endpoint_without_header(test_client_factory, async_client):
    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
    ) as client:
        response = client.get("/")

        assert response.status_code == 401


async def test_cannot_access_endpoint_with_invalid_header(test_client_factory, async_client):
    time = datetime.now() + timedelta(seconds=1)
    token = await get_user_and_token(time=time)

    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
    ) as client:
        response = client.get("/", headers={jwt_config.authorization_header: token})

        assert response.status_code == 401


async def test_cannot_access_endpoint_with_invalid_token(test_client_factory, async_client):
    time = datetime.now() + timedelta(seconds=1)
    token = await get_user_and_token(time=time)

    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)],
        raise_server_exceptions=False,
    ):
        response = await async_client.get(
            "/", headers={jwt_config.authorization_header: f"X_API {token}"}
        )
        assert response.status_code == 401


async def test_can_access_endpoint_with_valid_token(test_client_factory, async_client):
    time = datetime.now() + timedelta(minutes=20)
    token = await get_user_and_token(time=time)

    response = await async_client.get(
        "/", headers={jwt_config.authorization_header: f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "hello" in response.json()["message"]


async def test_can_access_endpoint_with_valid_token_after_login_failed(
    test_client_factory, async_client
):
    response = await async_client.get("/")

    assert response.status_code == 401

    # Create a user
    user_data = {
        "first_name": "Test",
        "last_name": "test",
        "email": "foo@bar.com",
        "password": _string_pass,
        "username": "test",
    }

    response = await async_client.post("/create", json=user_data)
    assert response.status_code == 201

    # login to get the JWT token
    user_login = {"email": user_data["email"], "password": user_data["password"]}
    response = await async_client.post("/login", json=user_login)
    assert response.status_code == 200

    access_token = response.json()["access_token"]

    # Access the home and return the logged in user email
    response = await async_client.get(
        "/", headers={jwt_config.authorization_header: f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"hello {user_data['email']}"}
