from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings
from esmerald.core.config.jwt import JWTConfig
from esmerald.contrib.auth.mongoz.middleware import JWTAuthMiddleware
from monkay import load
from lilya.middleware import DefineMiddleware as LilyaMiddleware

if TYPE_CHECKING:
    from esmerald.types import Middleware


class CustomSettings(EsmeraldAPISettings):
    @property
    def jwt_config(self) -> JWTConfig:
        """
        A JWT object configuration to be passed to the application middleware
        """
        return JWTConfig(
            signing_key=self.secret_key, auth_header_types=["Bearer", "Token"]
        )

    @property
    def middleware(self) -> List["Middleware"]:
        """
        Initial middlewares to be loaded on startup of the application.
        """
        return [
            LilyaMiddleware(
                JWTAuthMiddleware,
                config=self.jwt_config,
                user_model=load("myapp.models.User"),
            )
        ]
