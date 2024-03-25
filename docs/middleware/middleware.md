# Middleware

Esmerald includes several middleware classes unique to the application but also allowing some other ways of designing
them by using [protocols](../protocols.md). Inspired by other great frameworks, Esmerald has a similar approach
for the middleware protocol. Let's be honest, it is not that we can reinvent the wheel on something already working out
of the box.

There are two ways of designing the middleware for Esmerald. [Lilya middleware](#lilya-middleware) and
[Esmerald protocols](#esmerald-protocols) as both work quite well together.

## Lilya middleware

The Lilya middleware is the classic already available way of declaring the middleware within an **Esmerald**
application.

!!! Tip
    You can create a middleware like Lilya and add it into the application. To understand how to build them,
    Lilya has some great documentation <a href="https://www.lilya.dev/middleware/" target='_blank'>here</a>.

```python
{!> ../docs_src/middleware/starlette_middleware.py !}
```

The example above is for illustration purposes only as those middlewares are already in place based on specific
configurations passed into the application instance. Have a look at [CORSConfig](../configurations/cors.md),
[CSRFConfig](../configurations/csrf.md), [SessionConfig](../configurations/session.md) to understand how to use them
and automatically enable the built-in middlewares.

## Esmerald protocols

Esmerald protocols are not too different from the [Lilya middleware](#lilya-middleware). In fact,
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

The `MiddlewareProtocol` is simply an interface to build middlewares for **Esmerald** by enforcing the implementation of
the `__init__` and the `async def __call__`.

In the case of Esmerald configurations, a `config` parameter is declared and passed
in the `__init__` but this is not enforced on a protocol level but on a subclass level, the middleware itself.

Enforcing this protocol also aligns with writing
<a href='https://www.lilya.dev/middleware/#pure-asgi-middleware' target='_blank'>pure asgi middlewares</a>.

!!! Note
    MiddlewareProtocol does not enforce `config` parameters but enforces the `app` parameter as this will make sure
    it will also work with Lilya as well as used as standard.

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

## <a href='https://www.lilya.dev/middleware/#pure-asgi-middleware' target='_blank'>Writing ASGI middlewares</a>

**Esmerald** since follows the ASGI practices and uses Lilya underneath a good way of understand what can be
done with middleware and how to write some of them, Lilya also goes through with a lot of
<a href='https://www.lilya.dev/middleware/#writing-pure-asgi-middleware' target='_blank'>detail</a>.

## BaseAuthMiddleware

This is a very special middleware and it is the core for every authentication middleware that is used within
an **Esmerald** application.

`BaseAuthMiddleware` is also a protocol that simply enforces the implementation of the `authenticate` method and
assigning the result object into a `AuthResult` and make it available on every request.

### API Reference

Check out the [API Reference for BasseAuthMiddleware](../references/middleware/baseauth.md) for more details.

### Example of a JWT middleware class

```python title='/src/middleware/jwt.py'
{!> ../docs_src/middleware/auth_middleware_example.py !}
```

1. Import the `BaseAuthMiddleware` and `AuthResult` from `esmerald.middleware.authentication`.
2. Import `JWTConfig` to pass some specific and unique JWT configations into the middleware.
3. Implement the `authenticate` and assign the `user` result to the `AuthResult`.

!!! Info
    We use [Saffier](./../databases/saffier/motivation.md) for this example because Esmerald supports S
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
`lilya.middleware.DefineMiddleware` object to do it so. See `GZipMiddleware` [example](#middleware-and-the-settings).

If no parameters are needed, then you can simply pass the middleware class directly and Esmerald will take care of
the rest.

## Available middlewares

There are some available middlewares that are also available from Lilya.

* `CSRFMiddleware` - Handles with the CSRF and there is a [built-in](../configurations/csrf.md) how to enable.
* `CORSMiddleware` - Handles with the CORS and there is a [built-in](../configurations/cors.md) how to enable.
* `TrustedHostMiddleware` - Handles with the CORS if a given `allowed_hosts` is populated, the
[built-in](../configurations/cors.md) explains how to use it.
* `GZipMiddleware` - Same middleware as the one from Lilya.
* `HTTPSRedirectMiddleware` - Middleware that handles HTTPS redirects for your application. Very useful to be used
for production or production like environments.
* `RequestSettingsMiddleware` - The middleware that exposes the application settings in the request.
* `SessionMiddleware` - Same middleware as the one from Lilya.
* `WSGIMiddleware` - Allows to connect WSGI applications and run them inside Esmerald. A [great example](../wsgi.md)
how to use it is available.

### CSRFMiddleware

The default parameters used by the CSRFMiddleware implementation are restrictive by default and Esmerald allows some
ways of using this middleware depending of the taste.

```python
{!> ../docs_src/middleware/available/csrf.py !}
```

### CORSMiddleware

The default parameters used by the CORSMiddleware implementation are restrictive by default and Esmerald allows some
ways of using this middleware depending of the taste.

```python
{!> ../docs_src/middleware/available/cors.py !}
```

### RequestSettingsMiddleware

Exposes your Esmerald application settings in the request. This can be particulary useful to access
the main settings module in any part of the application,
inclusively [ChildEsmerald](../routing/router.md#child-esmerald-application).

This middleware has `settings` as optional parameter.
**If none is provided it will default to the internal settings**.

RequestSettingsMiddleware adds two types of settings to the request, the `global_settings` where is
the global Esmerald settings and the `app_settings` which corresponds to the
[settings_config](../application/settings.md#the-settings_config), if any,
passed to the Esmerald or ChildEsmerald instance.

```python hl_lines="6 8"
{!> ../docs_src/middleware/available/request_settings_middleware.py !}
```

### SessionMiddleware

Adds signed cookie-based HTTP sessions. Session information is readable but not modifiable.

```python
{!> ../docs_src/middleware/available/sessions.py !}
```

### HTTPSRedirectMiddleware

Like Lilya, enforces that all incoming requests must either be https or wss. Any http os ws will be redirected to
the secure schemes instead.

```python
{!> ../docs_src/middleware/available/https.py !}
```

### TrustedHostMiddleware

Enforces all requests to have a correct set `Host` header in order to protect against heost header attacks.

```python
{!> ../docs_src/middleware/available/trusted_hosts.py !}
```

### GZipMiddleware

Like Lilya, it handles GZip responses for any request that includes "gzip" in the Accept-Encoding header.

```python
{!> ../docs_src/middleware/available/gzip.py !}
```

### WSGIMiddleware

A middleware class in charge of converting a WSGI application into an ASGI one. There are some more examples
in the [WSGI Frameworks](../wsgi.md) section.

```python
{!> ../docs_src/middleware/available/wsgi.py !}
```

### Other middlewares

You can build your own middlewares as explained above but also reuse middlewares directly for Lilya if you wish.
The middlewares are 100% compatible.

Although some of the middlewares might mention Lilya or other ASGI framework, they are 100%
compatible with Esmerald as well.

#### <a href="https://github.com/abersheeran/asgi-ratelimit">RateLimitMiddleware</a>

A ASGI Middleware to rate limit and highly customizable.

#### <a href="https://github.com/snok/asgi-correlation-id">CorrelationIdMiddleware</a>

A middleware class for reading/generating request IDs and attaching them to application logs.

!!! Tip
    For Esmerald apps, just substitute FastAPI with Esmerald in the examples given or implement
    in the way Esmerald shows in this document.

#### <a href="https://github.com/steinnes/timing-asgi">TimingMiddleware</a>

ASGI middleware to record and emit timing metrics (to something like statsd).
This integration works using [EsmeraldTimming](https://github.com/dymmond/esmerald-timing).


## Important points

1. Esmerald supports [Lilya middleware](#lilya-middleware), [MiddlewareProtocol](#esmerald-protocols).
2. A MiddlewareProtocol is simply an interface that enforces `__init__` and `async __call__` to be implemented.
3. `app` is required parameter from any class inheriting from the `MiddlewareProtocol`.
4. <a href='https://www.lilya.dev/middleware/#pure-asgi-middleware' target='_blank'>Pure ASGI Middleware</a>
is encouraged and the `MiddlewareProtocol` enforces that.
5. Middleware classes can be added to any [layer of the application](#quick-note)
6. All authentication middlewares must inherit from the BaseAuthMiddleware.
7. You can load the **application middleware** in different ways.
