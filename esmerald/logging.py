from __future__ import annotations

import logging

from lilya.logging import (
    StandardLoggingConfig as LilyaStandardLoggingConfig,  # noqa
    logger as logger,  # noqa
)


class StandardLoggingConfig(LilyaStandardLoggingConfig):
    def get_logger(self) -> logging.Logger:
        return logging.getLogger("esmerald")
