from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.config import CSRFConfig
from esmerald.middleware import CSRFMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(CSRFMiddleware, secret="your-long-unique-secret")]

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
csrf_config = CSRFConfig(secret="your-long-unique-secret")

app = Esmerald(routes=routes, csrf_config=csrf_config)


# Option three - Using the settings module
# Running the application with your custom settings -> ESMERALD_SETTINGS_MODULE
class AppSettings(EsmeraldAPISettings):
    @property
    def csrf_config(self) -> CSRFConfig:
        return CSRFConfig(allow_origins=["*"])
