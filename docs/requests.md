# Request

While browsing the documentation a lot of examples where used using the `Request` object
from Esmerald.

Well, the `Request` is actually inherited from `Starlette` and some extas were added to tune it
to the needs of the framework.

Importing is as simple as:

```python
from esmerald import Request
```

## API Reference

You can learn more about the `Request` by checking the [API Reference](./references/request.md).

You can also read more about the `request` in the [Official Starlette documentation](https://www.lilya.dev/requests/).

## The Request

The `request` is what is used (generally) to get the data from the `path_parameters`, `cookies`, `headers`
or even the `user` current logged in.

As **Esmerald** uses `Starlette` under the hood, using the `Request` from it, it won't cause any
damage but you won't be able to access the whole scope of what **Esmerald** can do for you as well
as the unique way of handling the `.json()`.

Why this object then? Well, it is in the name, you might want to access the properties of the
`request` directly.

**Example**

```python
from esmerald import Esmerald, Gateway, get, Request


@get("/users/{id}")
def read_request(request: Request, id: str):
    host = request.client.host
    return {"host": host, "user_id": id}


app = Esmerald(
    routes=[
        Gateway(handler=read_request)
    ]
)
```

**Esmerald** automatically will know the *path parameters* of the handler by the way it is
declared but you can also access them via `request.path_params`.
