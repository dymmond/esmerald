from ravyn import Ravyn, RavynSettings
from ravyn.core.config import CSRFConfig
from ravyn.middleware import CSRFMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(CSRFMiddleware, secret="your-long-unique-secret")]

app = Ravyn(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
csrf_config = CSRFConfig(secret="your-long-unique-secret")

app = Ravyn(routes=routes, csrf_config=csrf_config)


# Option three - Using the settings module
# Running the application with your custom settings -> RAVYN_SETTINGS_MODULE
class AppSettings(RavynSettings):
    @property
    def csrf_config(self) -> CSRFConfig:
        return CSRFConfig(allow_origins=["*"])
