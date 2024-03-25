from typing import Any

import edgy
import pytest
from edgy.exceptions import ObjectNotFound
from jose.exceptions import JWTError
from lilya.types import ASGIApp

from esmerald import APIView, Gateway, HTTPException, Request, Response, get, settings, status
from esmerald.contrib.auth.edgy.base_user import AbstractUser
from esmerald.exceptions import NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.requests import Connection
from esmerald.security.jwt.token import Token
from esmerald.testclient import create_client

database, models = settings.edgy_registry
pytestmark = pytest.mark.anyio


class User(AbstractUser):
    """
    Inherits from the abstract user and adds the registry
    from esmerald settings.
    """

    is_confirm: bool = edgy.BooleanField(default=False)

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


def get_error_response(
    detail: Any,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> Response:
    raise HTTPException(
        detail=detail,
        status_code=status_code,
    )


class JWTAuthMiddleware(BaseAuthMiddleware):
    def __init__(self, app: "ASGIApp"):
        super().__init__(app)
        self.app = app
        self.config = settings.jwt_config

    async def retrieve_user(self, user_id) -> User:
        try:
            user_obj = await User.query.get(user_id=user_id)
            if user_obj.is_confirm and user_obj.is_active:
                return user_obj
        except ObjectNotFound:
            raise NotAuthorized() from None

    async def authenticate(self, request: Connection) -> AuthResult:
        try:
            # token_raw = request.headers.get(self.config.authorization_header, None)
            # token = token_raw.split(" ")[1] if token_raw else None

            token = request.headers.get(self.config.api_key_header, None)
            if not token:
                return get_error_response(
                    detail="Authentication failed",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            token = Token.decode(
                token=token,
                key=self.config.signing_key,
                algorithms=self.config.algorithm,
            )
            user = await self.retrieve_user(token.sub)
            return AuthResult(user=user)
        except JWTError:
            return get_error_response(
                detail="Authentication failed",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


@get()
async def home() -> str:
    return "home"


def test_middleware_can_be_added_on_top(test_client_factory):
    class UserAPIView(APIView):
        path = "/users"
        tags = ["User"]
        middleware = [JWTAuthMiddleware]

        @get(
            path="/",
        )
        async def all_users(self) -> Any: ...

        @get(
            path="/{user_id}",
            description="Get user data by id",
        )
        async def get_user_details(
            self,
            user_id: str,
            load_related: bool = False,
        ) -> Any: ...

        @get(
            path="/whoami",
            description="Get authenticated user data",
        )
        async def get_authenticated_user_data(
            self,
            request: Request,
        ) -> Any: ...

    with create_client(routes=[Gateway(handler=home), Gateway(handler=UserAPIView)]) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/users")
        assert response.status_code == 401

        response = client.get("/users/2")
        assert response.status_code == 401

        response = client.get("/users/25")
        assert response.status_code == 401

        response = client.get("/users/whoami")
        assert response.status_code == 401


def test_middleware_can_be_added_on_handler(test_client_factory):
    class AnotherUserAPIView(APIView):
        path = "/users"
        tags = ["User"]

        @get(path="/", middleware=[JWTAuthMiddleware])
        async def all_users(self) -> Any: ...

        @get(
            path="/{user_id}",
            description="Get user data by id",
        )
        async def get_user_details(
            self,
            user_id: str,
            load_related: bool = False,
        ) -> Any:
            return "Working when no middleware is here"

        @get(
            path="/whoami",
            description="Get authenticated user data",
        )
        async def get_authenticated_user_data(
            self,
            request: Request,
        ) -> Any:
            return "I'm dragonfly"

    with create_client(
        routes=[Gateway(handler=home), Gateway(handler=AnotherUserAPIView)]
    ) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/users")
        assert response.status_code == 401

        response = client.get("/users/2")
        assert response.status_code == 200
        assert response.json() == "Working when no middleware is here"

        response = client.get("/users/whoami")
        assert response.status_code == 200
        assert response.json() == "I'm dragonfly"


def test_middleware_can_be_added_on_both(test_client_factory):
    class UserView(APIView):
        path = "/users"
        tags = ["User"]
        middleware = [JWTAuthMiddleware]

        @get(path="/", middleware=[JWTAuthMiddleware])
        async def all_users(self) -> Any: ...

        @get(
            path="/{user_id}",
            description="Get user data by id",
        )
        async def get_user_details(
            self,
            user_id: str,
            load_related: bool = False,
        ) -> Any: ...

        @get(
            path="/whoami",
            description="Get authenticated user data",
        )
        async def get_authenticated_user_data(
            self,
            request: Request,
        ) -> Any: ...

    with create_client(routes=[Gateway(handler=home), Gateway(handler=UserView)]) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/users")
        assert response.status_code == 401

        response = client.get("/users/2")
        assert response.status_code == 401

        response = client.get("/users/25")
        assert response.status_code == 401

        response = client.get("/users/whoami")
        assert response.status_code == 401
