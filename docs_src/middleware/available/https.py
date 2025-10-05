from typing import List

from ravyn import Ravyn, RavynSettings
from ravyn.middleware import HTTPSRedirectMiddleware
from ravyn.types import Middleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(HTTPSRedirectMiddleware)]

app = Ravyn(routes=routes, middleware=middleware)


# Option two - Using the settings module
# Running the application with your custom settings -> RAVYN_SETTINGS_MODULE
class AppSettings(RavynSettings):
    @property
    def middleware(self) -> List["Middleware"]:
        # There is no need to wrap in a LilyaMiddleware here.
        # Ravyn automatically will do it once the application is up and running.
        return [HTTPSRedirectMiddleware]
