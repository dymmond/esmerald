# JWTConfig

JWT extends for JSON Web Token and it can be used with any middleware at your desire that implements the
[BaseAuthMiddleware](../middleware/middleware.md#baseauthmiddleware).

!!! Tip
    More information about JWT
    <a href="https://jwt.io/introduction" target='_blank'>here</a>.

## Requirements

Esmerald uses `python-jose` and `passlib` for this JWT integration. You can install by running:

```shell
$ pip install esmerald[jwt]
```

## JWTConfig and application

To use the JWTConfig with a middleware.

```python hl_lines="5 8-10 12"
{!> ../docs_src/configurations/jwt/example1.py!}
```

!!! info
    The example uses a supported [JWTAuthMiddleware](../databases/saffier/middleware.md#jwtauthmiddleware)
    from Esmerald with Saffier ORM.

## Parameters

All the parameters and defaults are available in the [JWTConfig Reference](../references/configurations/jwt.md).

## JWTConfig and application settings

The JWTConfig can be done directly via [application instantiation](#jwtconfig-and-application) but also via settings.

```python
{!> ../docs_src/configurations/jwt/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

## Token model

Esmerald offers a pretty standard Token object that allows you to generate and decode tokens at ease.

```python
from esmerald.security.jwt.token import Token

token = Token(exp=..., iat=..., sub=...)
```

The parameters are pretty standard from
<a href="https://python-jose.readthedocs.io/en/latest/" target='_blank'>Python JOSE</a> so you can feel
confortable with.

### Generate a Token (encode)

The [token](#token-model) offers simple and standard operations to interact with `python-jose`.

```python
from esmerald.security.jwt.token import Token
from esmerald.conf import settings

# Create the token model
token = Token(exp=..., iat=..., sub=...)

# Generate the JWT token
jwt_token = Token.encode(key=settings.secret_key, algorithm="HS256", **claims)
```

### Decode a Token (encode)

The same decoding functionality is also provided.

```python
from esmerald.security.jwt.token import Token
from esmerald.conf import settings

# Decodes the JWT token
jwt_token = Token.decode(token=..., key=settings.secret_key, algorithms=["HS256"])
```

The `Token.decode` returns a [Token](#token-model) object.

!!! Note
    This functionality relies heavily on `python-jose` but it is not mandatory to use it in any way.
    You are free to use any library that suits your unique needs. Esmerald only offers some examples and alternatives.
