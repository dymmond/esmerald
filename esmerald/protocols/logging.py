from typing import Any, TypeVar

from typing_extensions import Protocol, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class LoggingProtocol(Protocol):  # pragma: no cover
    def info(self, *args: Any, **kwargs: Any) -> None: ...

    def debug(self, *args: Any, **kwargs: Any) -> None: ...

    def warning(self, *args: Any, **kwargs: Any) -> None: ...

    def error(self, *args: Any, **kwargs: Any) -> None: ...

    def critical(self, *args: Any, **kwargs: Any) -> None: ...
