from typing import List

from ravyn import Ravyn, RavynSettings
from ravyn.middleware.security import SecurityMiddleware
from lilya.middleware import DefineMiddleware

routes = [...]

content_policy_dict = {
    "default-src": "'self'",
    "img-src": [
        "*",
        "data:",
    ],
    "connect-src": "'self'",
    "script-src": "'self'",
    "style-src": ["'self'", "'unsafe-inline'"],
    "script-src-elem": [
        "https://unpkg.com/@stoplight/elements/web-components.min.jss",
    ],
    "style-src-elem": [
        "https://unpkg.com/@stoplight/elements/styles.min.css",
    ],
}

# Option one
middleware = [DefineMiddleware(SecurityMiddleware, content_policy=content_policy_dict)]

app = Ravyn(routes=routes, middleware=middleware)


# Option two - Using the settings module
# Running the application with your custom settings -> RAVYN_SETTINGS_MODULE
class AppSettings(RavynSettings):
    def middleware(self) -> List[DefineMiddleware]:
        return [
            DefineMiddleware(SecurityMiddleware, content_policy=content_policy_dict),
        ]
