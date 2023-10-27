# **`StaticFilesConfig`** class

Reference for the `StaticFilesConfig` class object and how to use it.

Read more about [how to use the StaticFilesConfig](https://esmerald.dev/configurations/cors/) in your
application and leverage the system.

## How to import

```python
from esmerald import StaticFilesConfig
```

::: esmerald.config.static_files.StaticFilesConfig
    options:
        filters:
        - "!^validate_path"
        - "!^to_app"
        - "!^_build_kwargs"
