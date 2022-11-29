import logging
from types import FrameType
from typing import cast

from loguru import logger as loguru_logger

logger = logging.getLogger("esmerald")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str = loguru_logger.level(record.levelname).name
        except ValueError:
            level: str = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )
