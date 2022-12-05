from typing import Generic, TypeVar

from starlette.requests import HTTPConnection
from starlette.types import ASGIApp
from tortoise.exceptions import DoesNotExist

from esmerald.config import JWTConfig
from esmerald.exceptions import NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.security.jwt.token import Token

T = TypeVar("T")


class JWTAuthMiddleware(BaseAuthMiddleware):
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        app: "ASGIApp",
        config: "JWTConfig",
        user_model: Generic[T],
    ):
        super().__init__(app)
        """
        The user is simply the class type to be queried from the Tortoise ORM.

        Example how to use:

            1. User table

                from esmerald.contrib.auth.tortoise.base_user import User as BaseUser

                class User(BaseUser):
                    ...

            2. Middleware

                from esmerald.contrib.auth.tortoise.middleware import JWTAuthMiddleware
                from esmerald.config import JWTConfig

                jwt_config = JWTConfig(...)

                class CustomJWTMidleware(JWTAuthMiddleware):
                    def __init__(self, app: "ASGIApp"):
                        super().__init__(app, config=jwt_config, user=User)

            3. The application
                from esmerald import Esmerald
                from myapp.middleware import CustomJWTMidleware

                app = Esmerald(routes=[...], middleware=[CustomJWTMidleware])

        """
        self.app = app
        self.config = config
        self.user_model = user_model

    async def retrieve_user(self, user_id: int) -> Generic[T]:
        """
        Retrieves a user from the database using the given token id.
        """
        try:
            await self.user_model.get(pk=user_id)
        except DoesNotExist:
            raise NotAuthorized()

    async def authenticate(self, request: HTTPConnection) -> AuthResult:
        token = request.headers.get(self.config.api_key_header)

        if not token:
            raise NotAuthorized("JWT token not found.")

        token = Token.decode(
            token=token, key=self.config.signing_key, algorithm=self.config.algorithm
        )

        user = await self.retrieve_user(token.sub)
        return AuthResult(user=user)
