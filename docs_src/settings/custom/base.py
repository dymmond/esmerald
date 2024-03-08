from __future__ import annotations

from esmerald import EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType
from esmerald.middleware.https import HTTPSRedirectMiddleware
from esmerald.types import Middleware
from lilya.middleware import DefineMiddleware


class AppSettings(EsmeraldAPISettings):
    # The default is already production but for this example
    # we set again the variable
    environment: bool = EnvironmentType.PRODUCTION
    debug: bool = False
    reload: bool = False

    @property
    def middleware(self) -> list[Middleware]:
        return [DefineMiddleware(HTTPSRedirectMiddleware)]
