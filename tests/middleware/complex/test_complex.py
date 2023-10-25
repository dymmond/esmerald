import pytest
from starlette.types import ASGIApp

from esmerald import Gateway, Request
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
    with create_client(routes=[Gateway(handler=UserView)]) as client:
        response = client.post("/users")

        assert response.status_code == 201

        response = client.get("/users")

        assert response.status_code == 401

        response = client.put("/users/2")

        assert response.status_code == 401
