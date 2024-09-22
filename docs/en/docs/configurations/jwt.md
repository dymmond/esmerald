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
{!> ../../../docs_src/configurations/jwt/example1.py!}
```

!!! info
    The example uses a supported [JWTAuthMiddleware](../databases/saffier/middleware.md#jwtauthmiddleware)
    from Esmerald with Saffier ORM.

## Parameters

All the parameters and defaults are available in the [JWTConfig Reference](../references/configurations/jwt.md).

## JWTConfig and application settings

The JWTConfig can be done directly via [application instantiation](#jwtconfig-and-application) but also via settings.

```python
{!> ../../../docs_src/configurations/jwt/settings.py!}
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
comfortable with.

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

### Decode a Token (decode)

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

### The claims

The `**claims` can be very useful mostly if you want to generate tokens for `access` and `refresh`.
When using the `claims` you can simply pass any extra parameter that once [decoded](#decode-a-token-decode)
it will be available to you to manipulate.

The [database integrations](../databases/edgy/example.md) shows an example how to do this simple
operations as examples but let us run a quick example.

We will be using a middleware and we will be generating a `access_token` and a `refresh_token`
for a given API.

Let us assume a few things.

* There is a `User` model inside an `accounts/models.py`.
* The controllers are placed inside `accounts/controllers.py`.
* We will be subclassing an exising [middleware](../databases/edgy/middleware.md) to make it easier.
* The `middleware` is placed inside an `accounts/middleware.py`
* The [JWTConfig](#jwtconfig) is inside a settings file already configured.
* The `Token` class will be subclassed to allow extra parameters like `token_type`.
* There is an [accounts/backends.py](#backend) file containing operations for the authentication and refreshing of the token.

### The token class

You can and should subclass the `Token` class if you want to add extra parameters for your own
purposes, for instance to have an extra `token_type` that indicates the if the token is `access`
or `refresh` or whatever you need to have that can be used in and for your claims.

Something like this:

```python
{!> ../../../docs_src/configurations/jwt/claims/token.py!}
```

This will be particularly useful in the next steps as we will be using the `token_type` to distinguish
between the `access_token` and the `refresh_token`.

#### The middleware

Let us use an existing middleware from the [contrib](../databases/edgy/middleware.md) to make it easier.
This middleware will serve **only for access** the APIs **and not for refreshing the token**.

!!! Tip
    Feel free to build your own, this is for explanation purposes.

```python
{!> ../../../docs_src/configurations/jwt/claims/middleware.py!}
```

There is a lot here happening but basically what are we doing?

* Checking for `token` in the header.
* Checking if the `token_type` is of `access_token` (default name from the JWTConfig and can be whatever you want) and raises
an exception if it's not `access_token`.
* Returns the `AuthResult` object with the details of the retrieved user.

The middleware also contains a wrapper called `AuthMiddleware`. This will be used later on in the views of the user.

#### Backend

This is where we will place the logic that handles the authentication and refreshing of the token.

!!! Warning
    The example below uses [Edgy](https://edgy.dymmond.com) from the [contrib](../databases/edgy/models.md)
    to make it simpler to explain and query.

```python
{!> ../../../docs_src/configurations/jwt/claims/backends.py!}
```

Quite a lot of code, right? Well yes but it is mostly logic used for authenticate and refresh the existing
token.

Did you see the `BackendAuthentication` and the `RefreshAuthentication`? Now this will be very useful.

The `RefreshAuthentication` is where we validate the `refresh_token`. Remember the [middleware](#the-middleware)
only allowing `access_token`? Well this is the reason why. The middleware will be used only
for APIs that require authentication and the `refresh_token`, usually by design, should only do that,
refresh and nothing else.

Since the refresh token already contains all the infomation needed to generate the new access token,
there is no need to query the `user` again and do the whole process.

The way the refresh token was designed and passed in the `claims` also allows us to directly use it
and generate the new `access_token`.

Remember the [Token](#the-token-class) we subclassed? This is where the `token_type` plays the role
in dictating which type of token is being validated and sent.

The `access_token` is sent via `headers` **as it should** and the `refresh_token` is sent via `POST`.

#### The views

Now it is time to assemble everything in the views where we will have:

* `/auth/create` - Endpoint to create the users.
* `/auth/signin` - Login endpoint for the user.
* `/auth/users` - Endpoint that returns a list of all users.
* `/auth/refresh-access` - The endpoint responsible **only for refreshing the access_token**.

In the end, something like this:


```python
{!> ../../../docs_src/configurations/jwt/claims/controllers.py!}
```

As you can see, we now assembled everything. The `/auth/users` requires authentication to have
access and the `/auth/refresh-access` will make sure that will return only the new `access_token`.
