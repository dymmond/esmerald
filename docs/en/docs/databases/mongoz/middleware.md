# Middleware

As part of the support, Esmerald developed an authentication middleware using python-jose allowing JWT integration
with the current [supported documents](./documents.md#user).

## JWTAuthMiddleware

This simple but effective middleware extends the [BaseAuthMiddleware](../../middleware/middleware.md#baseauthmiddleware)
and enables the authentication via JWT.

```python
from esmerald.contrib.auth.mongoz.middleware import JWTAuthMiddleware
```

### Parameters

* `app` - Any ASGI app instance. E.g.: Esmerald instance.
* `config` - An instance of [JWTConfig](../../configurations/jwt.md) object.
* `user` - The user class (not instance!) being used by the application.

## How to use it

There are different ways of calling this middleware in any Esmerald application.

### Via settings

```python
{!> ../../../docs_src/databases/mongoz/jwt/settings.py!}
```

### Via application instantiation

```python
{!> ../../../docs_src/databases/mongoz/middleware/example1.py !}
```

### Via overriding the JWTAuthMiddleware

=== "Via app instance"

    ```python
    {!> ../../../docs_src/databases/mongoz/middleware/example2.py !}
    ```

=== "Via app settings"

    ```python
    {!> ../../../docs_src/databases/mongoz/middleware/example3.py !}
    ```

{!> ../../../docs_src/_shared/databases_important_note.md !}
