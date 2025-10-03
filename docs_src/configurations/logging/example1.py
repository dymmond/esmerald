import sys

from typing import Any
import loguru

from ravyn import LoggingConfig, Ravyn


class LoguruConfig(LoggingConfig):
    def __init__(self, level: str, **kwargs):
        super().__init__(level=level, **kwargs)

    def configure(self):
        loguru.logger.remove()
        loguru.logger.add(
            sink=sys.stdout,
            level=self.level,
            format="{time} {level} {message}",
            colorize=True,
        )

    def get_logger(self) -> Any:
        return loguru.logger


logging_config = LoguruConfig(level="INFO")

app = Ravyn(logging_config=logging_config)
