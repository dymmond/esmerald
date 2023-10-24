# **`SessionConfig`** class

Reference for the `SessionConfig` class object and how to use it.

Read more about [how to use the SessionConfig](https://esmerald.dev/configurations/session/) in your
application and leverage the system.

## How to import

```python
from esmerald import SessionConfig
```

::: esmerald.config.session.SessionConfig
    options:
        members:
            - secret_key
            - path
            - session_cookie
            - max_age
            - https_only
            - same_site
            - validate_secret
        filters:
        - "!^model_config"
