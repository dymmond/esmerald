from ravyn import CORSConfig, RavynSettings
from ravyn.core.config import LoggingConfig
from myapp.logging import LoguruLoggingConfig


class CustomSettings(RavynSettings):
    @property
    def logging_config(self) -> LoggingConfig:
        return LoguruLoggingConfig(level="Debug")
