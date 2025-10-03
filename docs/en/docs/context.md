# Context

The `Context` is a beauty of an object unique to **Ravyn**. The `context` is a parameter that
can be used **inside the handlers only** and provides additional information to your handler
that you might need for any particular reason.

Importing is as simple as:

```python
from ravyn import Context
```

## API Reference

You can learn more about the `Context` by checking the [API Reference](./references/context.md).

## The Context

You can see the `context` as the `request context` of a given handler. This also means, when
a [handler](https://ravyn.dev/routing/handlers/) is declared all the information passed to it
is automatically accessible via `context.handler` parameter.

The `context` also provides access to the [`request`](./requests.md) object as well as the
[application settings](./application/settings.md) and other functions.

This means, if you want to pass a `request` and `context` you actually only need the `context`
directly as the request is already available inside but you can still pass both anyway.

**Example**

```python
from ravyn import Context, Ravyn, Gateway, get


@get("/users/{id}")
def read_context(context: Context, id: str):
    host = context.request.client.host

    context_data = context.get_context_data()
    context.add_to_context("name", "Ravyn")

    context_data = context.get_context_data()
    context_data.update({
        "host": host, "user_id": id
    })
    return context_data


app = Ravyn(
    routes=[
        Gateway(handler=read_request)
    ]
)
```

The `context` can be particularly useful if you want to access `handler` information that is not
available after the handler is instantiated, for example and can be very useful if you also want
to access the `context.settings` where the application settings are available, another versatile way
of accessing them.
