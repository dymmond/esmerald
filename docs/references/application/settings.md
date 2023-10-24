# **`EsmeraldAPISettings`** class

Reference for the `EsmeraldAPISettings` class object and how to use it.

Read more about [how to use the settings](https://esmerald.dev/application/settings/) in your
application and leverage the system.

The settings are used by **any Esmerald application** and used as the defaults for the
[Esmerald](../esmerald.md) class instance if nothing is provided.

## How to import

```python
from esmerald import settings
```

**Via conf**

```python
from esmerald.conf import settings
```

**Via application instance**

```python
from esmerald import Esmerald

app = Esmerald()
app.settings
```

::: esmerald.conf.global_settings.EsmeraldAPISettings
    options:
        filters:
        - "!^model_config"
        - "!^ipython_args"
        - "!^ptpython_config_file"
        - "!^async_exit_config"
