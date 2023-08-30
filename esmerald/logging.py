import logging

from loguru import logger as loguru_logger


class InterceptHandler(logging.Handler):  # pragma: no cover
    def emit(self, record: logging.LogRecord) -> None:
        level: str
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )
