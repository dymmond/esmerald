from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.config import CORSConfig
from esmerald.middleware import CORSMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

# Option one
middleware = [LilyaMiddleware(CORSMiddleware, allow_origins=["*"])]

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Activating the built-in middleware using the config.
cors_config = CORSConfig(allow_origins=["*"])

app = Esmerald(routes=routes, cors_config=cors_config)


# Option three - Using the settings module
# Running the application with your custom settings -> ESMERALD_SETTINGS_MODULE
class AppSettings(EsmeraldAPISettings):
    @property
    def cors_config(self) -> CORSConfig:
        return CORSConfig(allow_origins=["*"])
