from esmerald import CORSConfig, EsmeraldSettings
from esmerald.core.config import LoggingConfig
from myapp.logging import LoguruLoggingConfig


class CustomSettings(EsmeraldSettings):
    @property
    def logging_config(self) -> LoggingConfig:
        return LoguruLoggingConfig(level="Debug")
