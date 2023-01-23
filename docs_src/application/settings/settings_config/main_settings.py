from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings
from esmerald.middleware import RequestSettingsMiddleware

if TYPE_CHECKING:
    from esmerald.types import Middleware


# Create a ChildEsmeraldSettings object
class AppSettings(EsmeraldAPISettings):
    app_name: str = "my application"
    secret_key: str = "main secret key"

    @property
    def middleware(self) -> List["Middleware"]:
        return [RequestSettingsMiddleware]
