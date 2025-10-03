from typing import List

from ravyn import RavynSettings
from ravyn.middleware import GZipMiddleware, HTTPSRedirectMiddleware
from ravyn.types import Middleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware


class AppSettings(RavynSettings):
    @property
    def middleware(self) -> List["Middleware"]:
        """
        All the middlewares to be added when the application starts.
        """
        return [
            HTTPSRedirectMiddleware,
            LilyaMiddleware(GZipMiddleware, minimum_size=500, compresslevel=9),
        ]
