from typing import TYPE_CHECKING, List

from starlette.types import ASGIApp

from esmerald import EsmeraldAPISettings
from esmerald.conf import settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.edgy.middleware import JWTAuthMiddleware
from lilya._internal._module_loading import import_string

if TYPE_CHECKING:
    from esmerald.types import Middleware


class AppAuthMiddleware(JWTAuthMiddleware):
    """
    Overriding the JWTAuthMiddleware
    """

    jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

    def __init__(self, app: "ASGIApp"):
        super().__init__(
            app, config=self.jwt_config, user_model=import_string("myapp.models.User")
        )


class AppSettings(EsmeraldAPISettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [AppAuthMiddleware]
