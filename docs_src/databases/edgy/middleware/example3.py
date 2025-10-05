from typing import TYPE_CHECKING, List

from ravyn import RavynSettings
from ravyn.conf import settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
from monkay import load
from lilya.types import ASGIApp

if TYPE_CHECKING:
    from ravyn.types import Middleware


class AppAuthMiddleware(JWTAuthMiddleware):
    """
    Overriding the JWTAuthMiddleware
    """

    jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

    def __init__(self, app: "ASGIApp"):
        super().__init__(app, config=self.jwt_config, user_model=load("myapp.models.User"))


class AppSettings(RavynSettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [AppAuthMiddleware]
