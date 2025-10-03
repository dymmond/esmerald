from abc import ABC

from lilya.logging import LoggingConfig as LilyaLoggingConfig


class LoggingConfig(LilyaLoggingConfig, ABC):
    """
    An instance of [LoggingConfig](https://ravyn.dev/configurations/logging/).

    !!! Tip
        You can create your own `LoggingMiddleware` version and pass your own
        configurations. You don't need to use the built-in version although it
        is recommended to do it so.

    **Example**

    ```python
    from ravyn import Ravyn
    from ravyn.core.config import LoggingConfig

    logging_config = LoggingConfig()

    app = Ravyn(logging_config=logging_config)
    ```
    """

    ...
