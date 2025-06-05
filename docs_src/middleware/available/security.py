from typing import List

from esmerald import Esmerald, EsmeraldSettings
from esmerald.middleware.security import SecurityMiddleware
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

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Using the settings module
# Running the application with your custom settings -> ESMERALD_SETTINGS_MODULE
class AppSettings(EsmeraldSettings):
    def middleware(self) -> List[DefineMiddleware]:
        return [
            DefineMiddleware(SecurityMiddleware, content_policy=content_policy_dict),
        ]
