from typing import Any, TypeVar

import bson
from lilya.types import ASGIApp
from mongoz import DocumentNotFound

from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.common.middleware import CommonJWTAuthMiddleware
from esmerald.exceptions import AuthenticationError, NotAuthorized

T = TypeVar("T")

IDS = ["id", "pk", "_id"]


class JWTAuthMiddleware(CommonJWTAuthMiddleware):
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        app: "ASGIApp",
        config: "JWTConfig",
        user_model: T,
    ):
        super().__init__(app, config, user_model)
        """
        The user is simply the class type to be queried from the Saffier ORM.

        Example how to use:

            1. User table

                from esmerald.contrib.auth.saffier.base_user import User as BaseUser

                class User(BaseUser):
                    ...

            2. Middleware

                from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
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
        self.user_model: T = user_model

    async def retrieve_user(self, token_sub: Any) -> T:
        """
        Retrieves a user from the database using the given token id.
        """
        try:
            sub = int(token_sub)
            token_sub = sub
        except (TypeError, ValueError):
            ...  # noqa

        if isinstance(token_sub, str) and self.config.user_id_field in IDS:
            token_sub = bson.ObjectId(token_sub)

        user_field = {self.config.user_id_field: token_sub}
        try:
            return await self.user_model.objects.get(**user_field)  # type: ignore
        except DocumentNotFound:
            raise NotAuthorized() from None
        except Exception as e:
            raise AuthenticationError(detail=str(e)) from e
