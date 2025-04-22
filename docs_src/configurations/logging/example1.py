import sys

from typing import Any

from esmerald import LoggingConfig, Esmerald

class LoguruConfig(LoggingConfig):
    def __init__(self, level: str, **kwargs):
        self.level = level

    def configure(self):
        import loguru

        loguru.logger.remove()
        loguru.logger.add(
            sink=sys.stdout,
            level=self.level,
            format="{time} {level} {message}",
            colorize=True,
        )

    def get_logger(self) -> Any:
        import loguru

        return loguru.logger

logging_config = LoguruConfig(level="INFO")

app = Esmerald(logging_config=logging_config)
