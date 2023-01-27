from typing import Any, Generic, TypeVar

from jose import JWSError, JWTError
from starlette.authentication import AuthenticationError
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp
from tortoise.exceptions import DoesNotExist

from esmerald.config.jwt import JWTConfig
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

    async def retrieve_user(self, token_sub: Any) -> Generic[T]:
        """
        Retrieves a user from the database using the given token id.
        """
        user_field = {self.config.user_id_field: token_sub}
        try:
            return await self.user_model.get(**user_field)
        except DoesNotExist:
            raise NotAuthorized()

    async def authenticate(self, request: HTTPConnection) -> AuthResult:
        """
        Retrieves the header default of the config and validates against the decoding.

        Raises Authentication error if invalid.
        """
        token = request.headers.get(self.config.api_key_header.lower())

        if not token:
            raise NotAuthorized(detail="Token not found in the request header")

        token_partition = token.partition(" ")
        token_type = token_partition[0]
        auth_token = token_partition[-1]

        if token_type not in self.config.auth_header_types:
            raise NotAuthorized(detail=f"{token_type} is not an authorized header type")

        try:
            token = Token.decode(
                token=auth_token, key=self.config.signing_key, algorithms=[self.config.algorithm]
            )
        except (JWSError, JWTError) as e:
            raise AuthenticationError(str(e))

        user = await self.retrieve_user(token.sub)
        if not user:
            raise AuthenticationError("User not found")
        return AuthResult(user=user)
