# Test Client

Ravyn comes with a test client for your application tests. It is not mandatory use it as every application and
development team has its own way of testing it but just in case, it is provided.

## Requirements

This section requires the ravyn testing suite to be installed. You can do it so by running:

```shell
$ pip install ravyn[test]
```

## API Reference

Check the [API Reference for the test client](./references/test-client.md) to understand more.

## The test client

```python
{!> ../../../docs_src/testclient/example1.py !}
```

The test client is very similar to its original as it extends it and adds extra unique and specifics for `Ravyn`
and therefore the same examples and use cases will work.

You can use any of the `httpx` standard API like authentication, session cookies and file uploads.

```python
{!> ../../../docs_src/testclient/example2.py !}
```

And like Lilya, the same example to send files with `RavynTestClient`.

```python
{!> ../../../docs_src/testclient/example3.py !}
```

`httpx` is a great library created by the same author of `Django Rest Framework`.

!!! Info
    By default the RavynTestClient raise any exceptions that occur in the application.
    Occasionally you might want to test the content of 500 error responses, rather than allowing client to raise the
    server exception. In this case you should use `client = RavynTestClient(app, raise_server_exceptions=False)`.

## Lifespan events

!!! Note
    Ravyn supports all the lifespan events available and therefore `on_startup`, `on_shutdown` and `lifespan` are
    also supported by `RavynTestClient` **but** if you need to test these you will need to run `RavynTestClient`
    as a context manager or otherwise the events will not be triggered when the `RavynTestClient` is instantiated.

The framework also brings a ready to use functionality to be used as context manager for your tests.

### Context manager `create_client`

This function is prepared to be used as a context manager for your tests and ready to use at any given time.

```python
{!> ../../../docs_src/testclient/example4.py !}
```

The tests work with both `sync` and `async` functions.

!!! info
    The example above is used to also show the tests can be as complex as you desire and it will work with the
    context manager.

## override_settings

This is a special decorator from Lilya and serves as the helper for your tests when you need to update/change
the settings for a given test temporarily to test any scenario that requires specific settings to have different values.

The `override_settings` acts as a normal function decorator or as a context manager.

The settings you can override are the ones declared in the [settings](./application/settings.md).

```python
from ravyn.testclient import override_settings
```

Let us see an example.

```python
from lilya.middleware import DefineMiddleware

from ravyn import Ravyn, Gateway, get
from ravyn.middleware.clickjacking import XFrameOptionsMiddleware
from ravyn.responses import PlainText
from ravyn.testclient import override_settings


@override_settings(x_frame_options="SAMEORIGIN")
def test_xframe_options_same_origin_responses(test_client_factory):
    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(XFrameOptionsMiddleware)],
    )

    client = test_client_factory(app)

    response = client.get("/")

    assert response.headers["x-frame-options"] == "SAMEORIGIN"
```

Or as context manager.

```python
from lilya.middleware import DefineMiddleware

from ravyn import Ravyn, Gateway, get
from ravyn.middleware.clickjacking import XFrameOptionsMiddleware
from ravyn.responses import PlainText
from ravyn.testclient import override_settings


def test_xframe_options_same_origin_responses(test_client_factory):
    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    with override_settings(x_frame_options="SAMEORIGIN"):
        app = Lilya(
            routes=[Path("/", handler=homepage)],
            middleware=[DefineMiddleware(XFrameOptionsMiddleware)],
        )

        client = test_client_factory(app)

        response = client.get("/")

        assert response.headers["x-frame-options"] == "SAMEORIGIN"
```
