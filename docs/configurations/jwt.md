# JWTConfig

JWT extends for JSON Web Token and it can be used with any middleware at your desire that implements the
[BaseAuthMiddleware](../middleware/middleware.md#baseauthmiddleware).

!!! Tip
    More information about JWT
    <a href="https://jwt.io/introduction" target='_blank'>here</a>.

## JWTConfig and application

To use the JWTConfig with a middleware.

```python hl_lines="11 13"
{!> ../docs_src/configurations/jwt/example1.py!}
```

!!! info
    The example uses a supported [JWTAuthMiddleware](../databases/tortoise/middleware.md#jwtauthmiddleware)
    from Esmerald with Tortoise ORM.

## Parameters

* **signing_key** - The secret used to encode and generate the JWT Token. Having a centralized `secret` like in the
settings would be recommended as it would be the source of truth for any configuration needing a secret.

* **api_key_header** - API Key header for the jwt.

    <sup>Default: `X_API_TOKEN`</sup>

* **algorithm** - Algorithm used for the jwt token encoding/decoding.

    <sup>Default: `HS256`</sup>

* **access_token_lifetime** - Lifetime of the token after generation..

    <sup>Default: `timedelta(minutes=5)`</sup>

* **refresh_token_lifetime** - Lifetime of the generated refresh token..

    <sup>Default: `timedelta(days=1)`</sup>

* **auth_header_types** - Header to be sent with the token value.

    <sup>Default: `['Bearer']`</sup>

* **jti_claim** - Used to prevent the JWT from being relayed and relay attacks.

    <sup>Default: `jti`</sup>

* **verifying_key** - Verification key.

    <sup>Default: `""`</sup>

* **leeway** - Used for when there is a clock skww times.

    <sup>Default: `0`</sup>

* **sliding_token_lifetime** - A datetime.timedelta object which specifies how long sliding tokens are valid to prove
authentication. This timedelta value is added to the current UTC time during token generation to obtain the
token's default `exp` claim value.

    <sup>Default: `timedelta(minutes=5)`</sup>

* **sliding_token_refresh_lifetime** - A datetime.timedelta object which specifies how long sliding tokens are valid
to be refreshed. This timedelta value is added to the current UTC time during token generation to obtain the token's
default `exp` claim value.

    <sup>Default: `0`</sup>

* **user_id_field** - The database field from the user model that will be included in generated tokens to identify
users. It is recommended that the value of this setting specifies a field that does not normally change once its initial
value is chosen. For example, specifying a `username` or `email` field would be a poor choice since an account's
username or email might change depending on how account management in a given service is designed. This could allow a
new account to be created with an old username while an existing token is still valid which uses that username as a
user identifier.

    <sup>Default: `id`</sup>

* **user_id_claim** - The claim in generated tokens which will be used to store user identifiers. For example, a setting
value of 'user_id' would mean generated tokens include a `user_id` claim that contains the user's identifier.

    <sup>Default: `user_id`</sup>

* **access_token_name** - Name of the key for the access token.

    <sup>Default: `access_token`</sup>

* **refresh_token_name** - Name of the key for the refresh token.

    <sup>Default: `refresh_token`</sup>

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
claims = {"sub": token.sub, "exp": token.exp}
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
