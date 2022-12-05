from starlette.requests import HTTPConnection
from starlette.types import ASGIApp
from tortoise.exceptions import DoesNotExist

from esmerald.config import JWTConfig
from esmerald.contrib.auth.tortoise.base_user import User
from esmerald.exceptions import NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.security.jwt.token import Token


class JWTAuthMiddleware(BaseAuthMiddleware):
    def __init__(self, app: "ASGIApp", config: "JWTConfig"):
        super().__init__(app)
        self.app = app
        self.config = config

    async def retrieve_user(self, user_id) -> User:
        try:
            return await User.get(pk=user_id)
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
