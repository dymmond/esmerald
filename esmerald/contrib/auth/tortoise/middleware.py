from typing import Any, Generic, TypeVar

from starlette.types import ASGIApp
from tortoise.exceptions import DoesNotExist

from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.common.middleware import CommonJWTAuthMiddleware
from esmerald.exceptions import NotAuthorized

T = TypeVar("T")


class JWTAuthMiddleware(CommonJWTAuthMiddleware):
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        app: "ASGIApp",
        config: "JWTConfig",
        user_model: Generic[T],
    ):
        super().__init__(app, config, user_model)
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
            raise NotAuthorized() from None
