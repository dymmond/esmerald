from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
from lilya._internal._module_loading import import_string
from lilya.middleware import DefineMiddleware as LilyaMiddleware

if TYPE_CHECKING:
    from esmerald.types import Middleware


class CustomSettings(EsmeraldAPISettings):
    @property
    def jwt_config(self) -> JWTConfig:
        """
        A JWT object configuration to be passed to the application middleware
        """
        return JWTConfig(signing_key=self.secret_key, auth_header_types=["Bearer", "Token"])

    @property
    def middleware(self) -> List["Middleware"]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [
            LilyaMiddleware(
                JWTAuthMiddleware,
                config=self.jwt_config,
                user_model=import_string("myapp.models.User"),
            )
        ]
