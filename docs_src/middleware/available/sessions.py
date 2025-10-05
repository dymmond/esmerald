from ravyn import Ravyn, RavynSettings
from ravyn.core.config import SessionConfig
from ravyn.middleware.sessions import SessionMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(SessionMiddleware, secret_key=...)]

app = Ravyn(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
session_config = SessionConfig(secret_key=...)

app = Ravyn(routes=routes, session_config=session_config)


# Option three - Using the settings module
# Running the application with your custom settings -> RAVYN_SETTINGS_MODULE
class AppSettings(RavynSettings):
    @property
    def session_config(self) -> SessionConfig:
        return SessionConfig(secret_key=...)
