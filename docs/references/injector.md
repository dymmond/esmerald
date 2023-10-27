# Inject, Factory and Injects

Esmerald dependency injection system is actually pretty simple and can
be checked in the [official dependency injection section](https://esmerald.dev/dependencies/)
for more details.

```python
from esmerald import Inject, Injects, Factory, DiderectInjects
```

::: esmerald.Inject
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"

::: esmerald.Injects
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"

::: esmerald.DirectInjects

::: esmerald.Factory
    options:
        filters:
        - "!^model_config"
        - "!^__hash__"
        - "!^__call__"
        - "!^__eq__"
