from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.config import SessionConfig
from esmerald.middleware import SessionMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(SessionMiddleware, secret_key=...)]

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
session_config = SessionConfig(secret_key=...)

app = Esmerald(routes=routes, session_config=session_config)


# Option three - Using the settings module
# Running the application with your custom settings -> ESMERALD_SETTINGS_MODULE
class AppSettings(EsmeraldAPISettings):
    @property
    def session_config(self) -> SessionConfig:
        return SessionConfig(secret_key=...)
