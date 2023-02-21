# Middleware

As part of the support, Esmerald developed an authentication middleware using python-jose allowing JWT integration
with the current [supported models](./models.md#user).

## JWTAuthMiddleware

This simple but effective middleware extends the [BaseAuthMiddleware](../../middleware/middleware.md#baseauthmiddleware)
and enables the authentication via JWT.

```python
from esmerald.contrib.auth.tortoise.middleware import JWTAuthMiddleware
```

### Parameters

* `app` - Any ASGI app instance. E.g.: Esmerald instance.
* `config` - An instance of [JWTConfig](../../configurations/jwt.md) object.
* `user` - The user class (not instance!) being used by the application.

## How to use it

There are different ways of calling this middleware in any Esmerald application.

### Via settings

```python
{!> ../docs_src/databases/tortoise/middleware/settings.py !}
```

### Via application instantiation

```python
{!> ../docs_src/databases/tortoise/middleware/example1.py !}
```

### Via overriding the JWTAuthMiddleware

=== "Via app instance"

    ```python
    {!> ../docs_src/databases/tortoise/middleware/example2.py !}
    ```

=== "Via app settings"

    ```python
    {!> ../docs_src/databases/tortoise/middleware/example3.py !}
    ```

### Important note

In the examples you could see sometimes the `StarletteMiddleware` being used and in other you didn't. The reason behind
is very simple and also explained in the [middleware section](../../middleware/middleware.md#important).

If you need to specify parameters in your middleware then you will need to wrap it in a`starlette.middleware.Middleware`
object to do it so.

If no parameters are needed, then you can simply pass the middleware class directly and Esmerald will take care of the
rest.
