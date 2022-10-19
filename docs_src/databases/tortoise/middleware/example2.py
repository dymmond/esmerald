from starlette.types import ASGIApp

from esmerald import Esmerald, JWTConfig
from esmerald.conf import settings
from esmerald.contrib.auth.tortoise.middleware import JWTAuthMiddleware
from esmerald.utils.module_loading import import_string


class AppAuthMiddleware(JWTAuthMiddleware):
    """
    Overriding the JWTAuthMiddleware
    """

    jwt_config = JWTConfig(signing_key=settings.secret, auth_header_types=["Bearer", "Token"])

    def __init__(self, app: "ASGIApp"):

        super().__init__(
            app, config=self.jwt_config, user_model=import_string("myapp.models.User")
        )


app = Esmerald(middleware=[AppAuthMiddleware])
