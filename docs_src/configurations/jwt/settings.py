from typing import TYPE_CHECKING, List

from ravyn import RavynSettings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware
from monkay import load

if TYPE_CHECKING:
    from ravyn.types import Middleware


class CustomSettings(RavynSettings):
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
                user_model=load("myapp.models.User"),
            )
        ]
