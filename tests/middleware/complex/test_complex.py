import pytest
from lilya.types import ASGIApp

from esmerald import Gateway, Include, Request
from esmerald.conf import settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.edgy.base_user import User as EdgyUser
from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
from esmerald.routing.handlers import get, post, put
from esmerald.routing.views import APIView
from esmerald.testclient import create_client

database, models = settings.edgy_registry
jwt_config = JWTConfig(signing_key="cenas", auth_header_types=["Bearer", "Token"])


class User(EdgyUser):
    class Meta:
        registry = models


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


class CustomJWTMidleware(JWTAuthMiddleware):
    def __init__(self, app: "ASGIApp"):
        super().__init__(app, config=jwt_config, user_model=User)


class UserView(APIView):
    """
    User management API View
    """

    path = "/users"

    @post(path="/")
    async def create(self) -> str:
        return "post"

    @get(path="/", middleware=[CustomJWTMidleware])
    async def get_current(self, request: Request) -> str:
        return "get"

    @put(path="/{id:int}", middleware=[CustomJWTMidleware])
    async def update_user(self, request: Request) -> str:
        return "put"


def test_can_access_endpoint(test_app_client_factory):
    with create_client(routes=[Gateway("/v1", handler=UserView)]) as client:
        response = client.post("/v1/users")

        assert response.status_code == 201

        response = client.get("/v1/users")

        assert response.status_code == 401

        response = client.put("/v1/users/2")

        assert response.status_code == 401


def test_can_access_endpoint_with_include(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[
                    Gateway("/v1", handler=UserView),
                ],
            )
        ]
    ) as client:
        response = client.post("/v1/users")

        assert response.status_code == 201

        response = client.get("/v1/users")

        assert response.status_code == 401

        response = client.put("/v1/users/2")

        assert response.status_code == 401


def test_can_access_endpoint_with_include_nested(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[
                    Include(
                        routes=[
                            Gateway("/v1", handler=UserView),
                        ],
                    )
                ]
            )
        ]
    ) as client:
        response = client.post("/v1/users")

        assert response.status_code == 201

        response = client.get("/v1/users")

        assert response.status_code == 401

        response = client.put("/v1/users/2")

        assert response.status_code == 401


class AnotherUserView(APIView):
    """
    User management API View
    """

    path = "/users"
    middleware = [CustomJWTMidleware]

    @post(path="/")
    async def create(self) -> str:
        return "post"

    @get(path="/")
    async def get_current(self, request: Request) -> str:
        return "get"

    @put(path="/{id:int}")
    async def update_user(self, request: Request) -> str:
        return "put"


def test_can_access_endpoint_blocked(test_app_client_factory):
    with create_client(routes=[Gateway(handler=AnotherUserView)]) as client:
        response = client.post("/users")

        assert response.status_code == 401

        response = client.get("/users")

        assert response.status_code == 401

        response = client.put("/users/2")

        assert response.status_code == 401


def test_can_access_endpoint_blocked_with_include(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[
                    Gateway(handler=AnotherUserView),
                ],
            )
        ]
    ) as client:
        response = client.post("/users")

        assert response.status_code == 401

        response = client.get("/users")

        assert response.status_code == 401

        response = client.put("/users/2")

        assert response.status_code == 401


def test_can_access_endpoint_blocked_with_include_nested(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[
                    Include(
                        routes=[
                            Gateway(handler=AnotherUserView),
                        ],
                    )
                ]
            )
        ]
    ) as client:
        response = client.post("/users")

        assert response.status_code == 401

        response = client.get("/users")

        assert response.status_code == 401

        response = client.put("/users/2")

        assert response.status_code == 401
