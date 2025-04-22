from __future__ import annotations

from typing import Any, cast

from esmerald.protocols.logging import LoggerProtocol


class LoggerProxy:
    """
    Proxy for the real logger used by Esmerald.
    """

    def __init__(self) -> None:
        self._logger: LoggerProtocol | None = None

    def bind_logger(self, logger: LoggerProtocol | None) -> None:  # noqa
        self._logger = logger

    def __getattr__(self, item: str) -> Any:
        if not self._logger:
            raise RuntimeError("Logger is not configured yet. Please call setup_logging() first.")
        return getattr(self._logger, item)


logger: LoggerProtocol = cast(LoggerProtocol, LoggerProxy())
