import threading
from typing import Any

import loguru
import pytest
import structlog
from lilya.logging import setup_logging
from loguru import logger as loguru_logger

from ravyn.core.config import LoggingConfig


# Simulate a clean logger for each test
def reset_global_logger():
    from ravyn import logging as ravyn_logging

    ravyn_logging.logger.bind_logger(None)


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
    from ravyn.logging import logger

    logger.debug("Debug message from Loguru")
    logger.info("Info message from Loguru")

    assert any("Debug message from Loguru" in message for message in sink)
    assert any("Info message from Loguru" in message for message in sink)


def test_structlog_logger_capture():
    sink = []
    setup_logging(CustomStructlogLoggingConfig(sink_list=sink))

    from ravyn.logging import logger

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

    from ravyn.logging import logger

    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")


@pytest.mark.parametrize(
    "level", [None, "lilya", 1, 2.5, "5-da"], ids=["none", "str", "int", "float", "str-int"]
)
def test_raises_assert_error(level):
    with pytest.raises(AssertionError):

        class CustomLog(LoggingConfig):
            def __init__(self):
                super().__init__(level=level)

            def configure(self) -> None:
                return None

            def get_logger(self) -> Any:
                return structlog.get_logger(__name__)

        CustomLog()


def test_concurrent_logging_after_initial_setup():
    """
    Verify that, once setup_logging() has been called,
    multiple threads can log concurrently without ever raising,
    and that all messages make it into the sink.
    """
    sink: list[str] = []
    # initial bind
    setup_logging(CustomLoguruLoggingConfig(sink_list=sink))

    errors: list[Exception] = []

    def worker():
        from lilya.logging import logger

        for _ in range(1000):
            try:
                logger.info("thread-safe test")
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No errors should have occurred
    assert not errors

    # 5 threads × 1000 messages each
    assert len(sink) == 5000


def test_rebinding_during_logging_keeps_all_threads_happy():
    """
    Phase 1: everyone logs under config1, then hits barrier1.
    Binder waits on barrier1, then rebinds to config2, then hits barrier2.
    Phase 2: everyone waits on barrier2, then logs under config2.

    This guarantees no race against `_logger is None`,
    and that both sinks see at least one message.
    """
    sink1: list[str] = []
    sink2: list[str] = []
    config1 = CustomLoguruLoggingConfig(sink_list=sink1)
    config2 = CustomLoguruLoggingConfig(sink_list=sink2)

    # 1) Bind the first logger before starting any threads
    setup_logging(config1)

    errors: list[Exception] = []
    num_workers = 5
    # workers + binder
    barrier1 = threading.Barrier(num_workers + 1)
    barrier2 = threading.Barrier(num_workers + 1)

    def binder():
        # wait until all workers have finished Phase 1
        barrier1.wait()
        # do the rebind
        setup_logging(config2)
        # let everyone proceed to Phase 2
        barrier2.wait()

    def worker():
        from lilya.logging import logger

        # Phase 1
        for _ in range(500):
            try:
                logger.info("phase1")
            except Exception as e:
                errors.append(e)
        # sync with binder
        barrier1.wait()

        # Phase 2
        barrier2.wait()
        for _ in range(500):
            try:
                logger.info("phase2")
            except Exception as e:
                errors.append(e)

    # launch
    binder_thread = threading.Thread(target=binder)
    workers = [threading.Thread(target=worker) for _ in range(num_workers)]
    for w in workers:
        w.start()
    binder_thread.start()

    # join
    for w in workers:
        w.join()
    binder_thread.join()

    # Assertions
    assert not errors, f"Threads saw errors: {errors}"
    assert any("phase1" in msg for msg in sink1), "No phase1 logs in sink1"
    assert any("phase2" in msg for msg in sink2), "No phase2 logs in sink2"
