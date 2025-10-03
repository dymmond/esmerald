from ravyn import Ravyn, RavynSettings
from ravyn.core.config import CORSConfig
from ravyn.middleware import CORSMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(CORSMiddleware, allow_origins=["*"])]

app = Ravyn(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
cors_config = CORSConfig(allow_origins=["*"])

app = Ravyn(routes=routes, cors_config=cors_config)


# Option three - Using the settings module
# Running the application with your custom settings -> RAVYN_SETTINGS_MODULE
class AppSettings(RavynSettings):
    @property
    def cors_config(self) -> CORSConfig:
        return CORSConfig(allow_origins=["*"])
