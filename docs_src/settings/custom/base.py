from __future__ import annotations

from ravyn import RavynSettings
from ravyn.conf.enums import EnvironmentType
from ravyn.middleware.https import HTTPSRedirectMiddleware
from ravyn.types import Middleware
from lilya.middleware import DefineMiddleware


class AppSettings(RavynSettings):
    # The default is already production but for this example
    # we set again the variable
    environment: str = EnvironmentType.PRODUCTION
    debug: bool = False
    reload: bool = False

    @property
    def middleware(self) -> list[Middleware]:
        return [DefineMiddleware(HTTPSRedirectMiddleware)]
