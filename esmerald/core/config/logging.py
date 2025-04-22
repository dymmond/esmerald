from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import Annotated, Doc, Literal


class LoggingConfig(ABC):
    """
    An instance of [LoggingConfig](https://esmerald.dev/configurations/logging/).

    !!! Tip
        You can create your own `LoggingMiddleware` version and pass your own
        configurations. You don't need to use the built-in version although it
        is recommended to do it so.

    **Example**

    ```python
    from esmerald import Esmerald
    from esmerald.core.config import LoggingConfig

    logging_config = LoggingConfig()

    app = Esmerald(logging_config=logging_config)
    ```
    """

    def __init__(
        self,
        level: Annotated[
            Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            Doc(
                """
                The logging level.
                """
            ),
        ] = "DEBUG",
        **kwargs: Any,
    ) -> None:
        self.level = level

    @abstractmethod
    def configure(self) -> None:
        """
        Configures the logging settings.
        """
        raise NotImplementedError("`configure()` must be implemented in subclasses.")

    @abstractmethod
    def get_logger(self) -> Any:
        """
        Returns the logger instance.
        """
        raise NotImplementedError("`get_logger()` must be implemented in subclasses.")
