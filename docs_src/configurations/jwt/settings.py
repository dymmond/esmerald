from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings, JWTConfig
from esmerald.contrib.auth.tortoise.middleware import JWTAuthMiddleware
from esmerald.utils.module_loading import import_string
from starlette.middleware import Middleware as StarletteMiddleware

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
            StarletteMiddleware(
                JWTAuthMiddleware,
                config=self.jwt_config,
                user_model=import_string("myapp.models.User"),
            )
        ]
