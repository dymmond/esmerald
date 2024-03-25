# Status Codes

You can import the `status` module from `esmerald`:

```python
from esmerald import status
```

The `status` is provided by Lilya which means you can also:

```python
from lilya import status
```

By default, the Esmerald [handlers](https://esmerald.dev/routing/handlers/) take care of the
`status_code` for you but you can always override the defaults and use your own.

## Example

```python
from typing import List, Dict

from esmerald import Esmerald, get, status, Gateway


@get('/users', status_code=status.HTTP_208_ALREADY_REPORTED)
async def all_users() -> List[Dict[str, str]]:
    return [{"name": "Natasha"}, {"name": "Tony"}, {"name": "Bruce"}]


app = Esmerald(
    routes=[
        Gateway(handler=all_users)
    ]
)
```

This will make sure that instead of returning `200` as default from `@get()`, it will return
`208` instead.

::: esmerald.status
