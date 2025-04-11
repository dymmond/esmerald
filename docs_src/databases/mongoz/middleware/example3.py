from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings
from esmerald.conf import settings
from esmerald.core.config.jwt import JWTConfig
from esmerald.contrib.auth.mongoz.middleware import JWTAuthMiddleware
from monkay import load
from lilya.types import ASGIApp

if TYPE_CHECKING:
    from esmerald.types import Middleware


class AppAuthMiddleware(JWTAuthMiddleware):
    """
    Overriding the JWTAuthMiddleware
    """

    jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

    def __init__(self, app: "ASGIApp"):
        super().__init__(app, config=self.jwt_config, user_model=load("myapp.models.User"))


class AppSettings(EsmeraldAPISettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [AppAuthMiddleware]
