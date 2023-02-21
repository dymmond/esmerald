# Event handlers

Esmerald provides also two event handlers that you can use in your application to start your database.

## on_startup/on_shutdown

Starting a databse with Tortoise is easy but sometimes can be somewhat messy to understand what and how to place
things.

Since Esmerald allows both parameters on an application instantiation and via settings you can then leverage that
and use the already built events for Tortoise.

### Start and stop via application and settings

The way you pass the configurations to tortoise is up to you, in this example we will be using a dictionary
to make it clear and in one place.

### Tortoise settings

```python title='src/configs/database/settings.py'
import os

from esmerald.conf import settings


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.environ.get("POSTGRES_HOST", "localhost"),
                "port": os.environ.get("POSTGRES_PORT", "5432"),
                "user": os.environ.get("POSTGRES_USER", "postgres"),
                "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
                "database": os.environ.get("POSTGRES_DB", "myapp"),
            },
        },
    },
    "apps": {
        "accounts": {
            "models": ["accounts.models", "aerich.models"],
            "connection": "default",
        },
    },
    "use_tz": settings.use_tz,
    "timezone": setings.timezone,
}

```

### Via application instance

```python
{!> ../docs_src/databases/tortoise/event_handlers/application.py !}
```

### Via settings

```python
{!> ../docs_src/databases/tortoise/event_handlers/settings.py !}
```
