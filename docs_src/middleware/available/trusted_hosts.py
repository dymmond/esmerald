from typing import List

from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.middleware import TrustedHostMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [
    LilyaMiddleware(TrustedHostMiddleware, allowed_hosts=["www.example.com", "*.example.com"])
]

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
allowed_hosts = ["www.example.com", "*.example.com"]

app = Esmerald(routes=routes, allowed_hosts=allowed_hosts)


# Option three - Using the settings module
# Running the application with your custom settings -> ESMERALD_SETTINGS_MODULE
class AppSettings(EsmeraldAPISettings):
    allowed_hosts: List[str] = ["www.example.com", "*.example.com"]
