from typing import TypeVar

from jose import JWSError, JWTError
from lilya._internal._connection import Connection
from lilya.types import ASGIApp

from esmerald.config.jwt import JWTConfig
from esmerald.exceptions import AuthenticationError, NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.security.jwt.token import Token

T = TypeVar("T")


class CommonJWTAuthMiddleware(BaseAuthMiddleware):  # pragma: no cover
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        config: "JWTConfig",
        user_model: T,
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

    async def authenticate(self, request: Connection) -> AuthResult:
        """
        Retrieves the header default of the config and validates against the decoding.

        Raises Authentication error if invalid.
        """
        token = request.headers.get(self.config.authorization_header, None)

        if not token or token is None:
            raise NotAuthorized(detail="Token not found in the request header")

        token_partition = token.partition(" ")
        token_type = token_partition[0]
        auth_token = token_partition[-1]

        if token_type not in self.config.auth_header_types:
            raise NotAuthorized(detail=f"'{token_type}' is not an authorized header.")

        try:
            token = Token.decode(
                token=auth_token,
                key=self.config.signing_key,
                algorithms=[self.config.algorithm],
            )
        except (JWSError, JWTError) as e:
            raise AuthenticationError(str(e)) from e

        user = await self.retrieve_user(token.sub)
        if not user:
            raise AuthenticationError("User not found.")
        return AuthResult(user=user)
