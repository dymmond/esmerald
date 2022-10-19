from typing import List

from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import EsmeraldAPISettings
from esmerald.middleware import GZipMiddleware, HTTPSRedirectMiddleware
from esmerald.types import Middleware


class AppSettings(EsmeraldAPISettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        All the middlewares to be added when the application starts.
        """
        return [
            HTTPSRedirectMiddleware,
            StarletteMiddleware(GZipMiddleware, minimum_size=500, compresslevel=9),
        ]
