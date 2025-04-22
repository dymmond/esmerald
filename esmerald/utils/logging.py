from __future__ import annotations

import logging.config
from typing import Any

from esmerald.core.config.logging import LoggingConfig
from esmerald.logging import logger as global_logger


class StandardLoggingConfig(LoggingConfig):
    def __init__(self, config: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.config = config or self.default_config()

    def default_config(self) -> dict[str, Any]:  # noqa
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "level": self.level,
                "handlers": ["console"],
            },
        }

    def configure(self) -> None:
        logging.config.dictConfig(self.config)

    def get_logger(self) -> Any:
        return logging.getLogger("esmerald")


def setup_logging(logging_config: LoggingConfig | None = None) -> None:
    """
    Sets up the logging system for the application.

    If a custom `LoggingConfig` is provided, it will be used to configure
    the logging system. Otherwise, a default `StandardLoggingConfig` will be applied.

    This allows full flexibility to use different logging backends such as
    the standard Python `logging`, `loguru`, `structlog`, or any custom
    implementation based on the `LoggingConfig` interface.

    Args:
        logging_config: An optional instance of `LoggingConfig` to customize
            the logging behavior. If not provided, the default standard logging
            configuration will be used.

    Raises:
        ValueError: If the provided `logging_config` is not an instance of `LoggingConfig`.
    """
    if logging_config is not None and not isinstance(logging_config, LoggingConfig):
        raise ValueError("`logging_config` must be an instance of LoggingConfig.")

    config = logging_config or StandardLoggingConfig()
    config.configure()

    # Gets the logger instance from the logging_config
    logger = config.get_logger()
    global_logger.bind_logger(logger)
