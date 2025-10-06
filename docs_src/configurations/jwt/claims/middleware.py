from jose import JWSError, JWTError

from ravyn.conf import settings
from ravyn.contrib.auth.edgy.middleware import (
    JWTAuthMiddleware as RavynMiddleware,
)
from ravyn.exceptions import AuthenticationError, NotAuthorized
from ravyn.middleware.authentication import AuthResult
from ravyn.security.jwt.token import Token
from lilya._internal._connection import Connection
from monkay import load
from lilya.middleware import DefineMiddleware as LilyaMiddleware


class JWTAuthMiddleware(RavynMiddleware):
    def get_token(self, request: Connection) -> Token:
        """
        Gets the token from the headers.
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
        return token

    async def authenticate(self, request: Connection) -> AuthResult:
        """
        Retrieves the header default of the config, validates
        and returns the AuthResult.

        Raises Authentication error if invalid.
        """
        token: Token = self.get_token(request)

        if token.token_type == settings.jwt_config.refresh_token_name:
            raise NotAuthorized(detail="Refresh tokens cannot be used for operations.")

        user = await self.retrieve_user(token.sub)
        if not user:
            raise AuthenticationError("User not found.")
        return AuthResult(user=user)


# Middleware responsible from user accesses.
# This can be imported in any level of the application
AuthMiddleware = LilyaMiddleware(
    JWTAuthMiddleware,
    config=settings.jwt_config,
    user_model=load("accounts.models.User"),
)
