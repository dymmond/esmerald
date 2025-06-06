from typing import List

from esmerald import EsmeraldSettings
from esmerald.middleware import GZipMiddleware, HTTPSRedirectMiddleware
from esmerald.types import Middleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware


class AppSettings(EsmeraldSettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        All the middlewares to be added when the application starts.
        """
        return [
            HTTPSRedirectMiddleware,
            LilyaMiddleware(GZipMiddleware, minimum_size=500, compresslevel=9),
        ]
