from esmerald import CORSConfig, EsmeraldAPISettings
from esmerald.core.config import LoggingConfig
from myapp.logging import LoguruLoggingConfig


class CustomSettings(EsmeraldAPISettings):
    @property
    def logging_config(self) -> LoggingConfig:
        return LoguruLoggingConfig(level="Debug")
