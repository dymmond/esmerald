import sys

from typing import Any

import loguru

from ravyn import LoggingConfig


class CustomLoggingConfig(LoggingConfig):
    def __init__(self, level: str, **kwargs):
        super().__init__(level=level, **kwargs)
        self.options = kwargs

    def configure(self):
        """
        Configures the logger by removing any existing handlers and adding a new one.
        """
        loguru.logger.remove()
        loguru.logger.add(
            sink=sys.stdout,
            level=self.level,
            format="{time} {level} {message}",
            colorize=True,
        )

    def get_logger(self) -> Any:
        """
        Returns the logger instance.
        """
        return loguru.logger
