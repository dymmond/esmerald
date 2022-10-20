# Middleware

Esmerald includes several middleware clases unique to the application but also allowing some other ways of designing
them by using [protocols](../protocols.md). Inspired by other great frameworks, Esmerald has a similar approach
for the middleware protocol. Let's be honest, it's not we can reinvent the wheel on something already working out 
of the box.

There are two ways of dedsigning the middleware for Esmerald. [Starlette middleware](#starlette-middleware) and
[Esmerald protocols](#esmerald-protocols) as both work quite well together.

## Starlette middleware

The Starlette middleware is the classic already available way of declaring the middleware within an **Esmerald**
application.

!!! Tip
    You can create a middleware like Starlette and add it into the application. To understand how to build them,
    Starlette has some great documentation <a href="https://www.starlette.io/middleware/" target='_blank'>here</a>.

```python
{!> ../docs_src/middleware/starlette_middleware.py !}
```

The example above is for illustration purposes only as those middlewares are already in place based on specific
configurations passed into the application instance. Have a look at [CORSConfig](../configurations/cors.md),
[CSRFConfig](../configurations/csrf.md), [SessionConfig](../configurations/session.md) to understand how to use them
and automatically enable the built-in middlewares.

## Esmerald protocols

Esmerald protocols are not too different from the [Starlette middleware](#starlette-middleware). In fact,
the name itself happens only because of the use of the
<a href="https://peps.python.org/pep-0544/" target="_blank">python protocols</a>
which forces a certain structure to happen and since **Esmerald** likes configurations as much as possible,
using a protocol helps enforcing that and allows a better design.

```python
{!> ../docs_src/middleware/protocols.py !}
```

### MiddlewareProtocol

For those coming from a more enforced typed language like Java or C#, a protocol is the python equivalent to an
interface.

The `MiddlewareProtocol` is simply an interface to build middlewares for **Esmerald** by enforcing the implemenation of
the `__init__` and the `async def __call__`.

In the case of Esmerald configurations, a `config` parameter is declared and passed
in the `__init__` but this is not enforced on a protocol level but on a subclass level, the middleware itself.

Enforcing this protocol also aligns with writting
<a href='https://www.starlette.io/middleware/#pure-asgi-middleware' target='_blank'>pure asgi middlewares</a>.

!!! Note
    MiddlewareProtocol does not enforce `config` parameters but enforces the `app` parameter as this will make sure
    it will also work with Starlette as well as used as standard.

### Quick sample

```python
{!> ../docs_src/middleware/sample.py !}
```

## MiddlewareProtocol and the application

Creating this type of middlewares will make sure the protocols are followed and therefore reducing development errors
by removing common mistakes.

To add middlewares to the application is very simple.

=== "Application level"

    ```python
    {!> ../docs_src/middleware/adding_middleware.py !}
    ```

=== "Any other level"

    ```python
    {!> ../docs_src/middleware/any_other_level.py !}
    ```

### Quick note

!!! Info
    The middleware is not limited to `Esmerald`, `ChildEsmerald`, `Include` and `Gateway`. They also work with
    `WebSocketGateway` and inside every [get](./../routing/handlers.md#get),
    [post](./../routing/handlers.md#post), [put](./../routing/handlers.md#put),
    [patch](./../routing/handlers.md#patch), [delete](./../routing/handlers.md#delete)
    and [route](./../routing/handlers.md#route) as well as [websocket](./../routing/handlers.md#websocket).
    We simply choose `Gateway` as it looks simpler to read and understand.

## <a href='https://www.starlette.io/middleware/#pure-asgi-middleware' target='_blank'>Writting ASGI middlewares</a>

**Esmerald** since follows the ASGI practices and uses Starlette underneath a good way of understand what can be
done with middleware and how to write some of them, Starlette also goes through with a lot of
<a href='https://www.starlette.io/middleware/#writing-pure-asgi-middleware' target='_blank'>detail</a>.

## BaseAuthMiddleware

This is a very special middleware and it's the core for every authentication middleware that is used within
an **Esmerald** application.

`BaseAuthMiddleware` is also a protocol that simply enforces the implementation of the `authenticate` method and
assigning the result object into a `AuthResult` and make it available on every request.

### Example of a JWT middleware class

```python title='/src/middleware/jwt.py'
{!> ../docs_src/middleware/auth_middleware_example.py !}
```

1. Import the `BaseAuthMiddleware` and `AuthResult` from `esmerald.middleware.authentication`.
2. Import `JWTConfig` to pass some specific and unique JWT configations into the middleware.
3. Implement the `authenticate` and assign the `user` result to the `AuthResult`.

!!! Info
    We use [Tortoise-ORM](./../databases/tortoise/tortoise.md) for this example because Esmerald supports tortoise
    and contains functionalities linked with that support (like the User table) but **Esmerald**
    **is not dependent of ANY specific ORM** which means that you are free to use whatever you prefer.

#### Import the middleware into an Esmerald application

=== "From the application instance"

    ```python
    from esmerald import Esmerald
    from .middleware.jwt import JWTAuthMiddleware


    app = Esmerald(routes=[...], middleware=[JWTAuthMiddleware])
    ```

=== "From the settings"

    ```python
    from typing import List

    from esmerald import EsmeraldAPISettings
    from esmerald.types import Middleware
    from .middleware.jwt import JWTAuthMiddleware


    class AppSettings(EsmeraldAPISettings):

        @property
        def middleware(self) -> List["Middleware"]:
            return [
                JWTAuthMiddleware
            ]

    # load the settings via ESMERALD_SETTINGS_MODULE=src.configs.live.AppSettings
    app = Esmerald(routes=[...])
    ```

!!! Tip
    To know more about loading the settings and the available properties, have a look at the
    [settings](./../application/settings.md) docs.

## Middleware and the settings

One of the advantages of Esmerald is leveraging the settings to make the codebase tidy, clean and easy to maintain.
As mentioned in the [settings](../application/settings.md) document, the middleware is one of the properties available
to use to start an Esmerald application.

```python title='src/configs/live.py'
{!> ../docs_src/middleware/settings.py !}
```

**Start the application with the new settings**


```shell
ESMERALD_SETTINGS_MODULE=configs.live.AppSettings uvicorn src:app

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

!!! attention
    If `ESMERALD_SETTINGS_MODULE` is not specified as the module to be loaded, **Esmerald** will load the default settings
    but your middleware will not be initialized.

### Important

If you need to specify parameters in your middleware then you will need to wrap it in a
`starlette.middleware.Middleware` object to do it so. See `GZipMiddleware` [example](#middleware-and-the-settings).

If no parameters are needed, then you can simply pass the middleware class directly and Esmerald will take care of
the rest.

## Important points

1. Esmerald supports [Starlette middleware](#starlette-middleware), [MiddlewareProtocol](#esmerald-protocols).
2. A MiddlewareProtocol is simply an interface that enforces `__init__` and `async __call__` to be implemented.
3. `app` is required parameter from any class inheriting from the `MiddlewareProtocol`.
4. <a href='https://www.starlette.io/middleware/#pure-asgi-middleware' target='_blank'>Pure ASGI Middleware</a>
is encouraged and the `MiddlewareProtocol` enforces that.
5. Middleware classes can be added to any [layer of the application](#quick-note)
6. All authentication middlewares must inherit from the BaseAuthMiddleware.
7. You can load the **application middleware** in different ways.
