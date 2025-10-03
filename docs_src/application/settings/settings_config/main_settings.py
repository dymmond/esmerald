from typing import TYPE_CHECKING, List

from ravyn import RavynSettings
from ravyn.middleware import RequestSettingsMiddleware

if TYPE_CHECKING:
    from ravyn.types import Middleware


# Create a ChildRavynSettings object
class AppSettings(RavynSettings):
    app_name: str = "my application"
    secret_key: str = "main secret key"

    @property
    def middleware(self) -> List["Middleware"]:
        return [RequestSettingsMiddleware]
