from typing import Optional

# LoggingConfig

## Why Esmerald Introduced `LoggingConfig`

In building applications, logging is one of the most crucial parts of observability, debugging, and monitoring.

Originally, Esmerald relied on developers manually configuring their own logging systems. However, to provide a consistent,
extensible, and framework-integrated way to handle logging, Esmerald introduced a first-class logging system built around
the `LoggingConfig` concept.

The goals of introducing `LoggingConfig` were:

- **Consistency**: Applications have a predictable and reliable way of setting up logging.
- **Flexibility**: Support standard Python logging, Loguru, Structlog, or any custom backend.
- **Simplicity**: Only one central logger (`esmerald.logging.logger`) needs to be imported and used across the entire app.
- **Extensibility**: Developers can easily subclass and provide their own custom logging configurations.

Esmerald now automatically configures a global `logger` instance, based on the `LoggingConfig` provided during startup.

---

## How `LoggingConfig` Works

`LoggingConfig` is an **abstract base class** that defines how to configure the logging system.

Esmerald provides:

- `StandardLoggingConfig` — for classic Python `logging`.

You can also implement your own custom logging backend by subclassing `LoggingConfig`.

When `setup_logging(logging_config)` is called during app startup (you don't have access to this as this is internal), Esmerald:

1. Applies the provided `LoggingConfig`.
2. Binds the global `esmerald.logging.logger` to the correct backend.

!!! Note
    After configuration, importing and using `from esmerald.logging import logger` will always point to the correct
    logging system automatically.

## Available Logging Backends

### 1. Standard Python Logging

Default behavior if nothing is specified.

```python
from esmerald import Esmerald

app = Esmerald()
```

Or inside `Esmerald` (with an example of a loguru logger):

```python
{!> ../../../docs_src/configurations/logging/example1.py!}
```

## Defining a Custom Logging Configuration

You can easily define your own `LoggingConfig` by subclassing it:

```python
{!> ../../../docs_src/configurations/logging/example2.py!}
```

When creating a custom logger **you must** declare the following methods:

- `configure()` - This method is called to set up the logging configuration.
- `get_logger()` - This method should return the logger instance.

These methods are called during the application startup process and will make sure the logger is set up correctly
using a common interface.

Usage:

```python
from esmerald import Esmerald

app = Esmerald(logging_config=CustomLoggingConfig())
```

## Using `logging_config` via `EsmeraldAPISettings`

If you are using settings classes to configure your app, you can pass the logging configuration there too:

```python
{!> ../../../docs_src/configurations/logging/settings.py!}
```

Then when initializing Esmerald:

```python
from esmerald import Esmerald

app = Esmerald(settings_config=AppSettings())
```

!!! Tip
    You can also initialise Esmerald settings via `ESMERALD_SETTINGS_MODULE` as you can see in [settings](../application/settings.md)
    documentation. This is useful for separating your settings from the application instance.

Esmerald will automatically extract and configure the logger from your settings class.

## Accessing the Global Logger

Anywhere in your project, simply do:

```python
from esmerald.logging import logger

logger.info("This is a log message.")
logger.error("This is an error log.")
```

No matter what backend you use (standard, Loguru, Structlog), the `logger` will behave correctly.

## Important Notes

- If you need to **reconfigure logging** during runtime (e.g., in tests), you should explicitly teardown/reset first.
- If no `logging_config` is provided, Esmerald defaults to a safe `StandardLoggingConfig`.


## Conclusion

`LoggingConfig` provides a powerful, flexible, and unified way to configure logging in Esmerald applications.

It ensures that regardless of the logging backend used, your app's logging behavior is predictable, extensible, and simple to maintain.
