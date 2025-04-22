from typing import Any

import loguru
import pytest
import structlog
from loguru import logger as loguru_logger

from esmerald.core.config import LoggingConfig
from esmerald.utils.logging import setup_logging


# Simulate a clean logger for each test
def reset_global_logger():
    from esmerald import logging as esmerald_logging

    esmerald_logging.logger.bind_logger(None)


@pytest.fixture(autouse=True)
def clean_logger():
    reset_global_logger()
    yield
    reset_global_logger()


class CustomLoguruLoggingConfig(LoggingConfig):
    def __init__(self, sink_list, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sink_list = sink_list

    def configure(self) -> None:
        loguru_logger.remove()
        loguru_logger.add(
            sink=self.sink_list.append,
            level=self.level,
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        )

    def get_logger(self) -> Any:
        return loguru.logger


class ListLogger:
    def __init__(self, sink: list[str]):
        self.sink = sink

    def info(self, event: str, **kwargs):
        self.sink.append(event)

    def debug(self, event: str, **kwargs):
        self.sink.append(event)

    def warning(self, event: str, **kwargs):
        self.sink.append(event)

    def error(self, event: str, **kwargs):
        self.sink.append(event)

    def critical(self, event: str, **kwargs):
        self.sink.append(event)


class CustomStructlogLoggingConfig(LoggingConfig):
    def __init__(self, sink_list, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sink_list = sink_list

    def configure(self) -> None:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger("info"),
            processors=[],
            context_class=dict,
            logger_factory=lambda *_: ListLogger(self.sink_list),
        )

    def get_logger(self) -> Any:
        return structlog.get_logger(__name__)


def test_loguru_logger_setup():
    sink = []
    setup_logging(CustomLoguruLoggingConfig(sink_list=sink))
    from esmerald.logging import logger

    logger.debug("Debug message from Loguru")
    logger.info("Info message from Loguru")

    assert any("Debug message from Loguru" in message for message in sink)
    assert any("Info message from Loguru" in message for message in sink)


def test_structlog_logger_capture():
    sink = []
    setup_logging(CustomStructlogLoggingConfig(sink_list=sink))

    from esmerald.logging import logger

    logger.info("Info message from Structlog")
    logger.error("Error message from Structlog")

    # The logs are captured as JSON strings in the sink
    assert any("Info message from Structlog" in message for message in sink)
    assert any("Error message from Structlog" in message for message in sink)


def test_invalid_logging_config():
    with pytest.raises(ValueError):
        setup_logging(logging_config="not_a_valid_config")


def test_standard_logging_fallback(monkeypatch):
    setup_logging()

    from esmerald.logging import logger

    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")
