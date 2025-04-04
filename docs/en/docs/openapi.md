---
hide:
  - navigation
---

# OpenAPI

Esmerald as mentioned across the documentation supports natively the automatic generation of the
API docs in three different ways:

* **Swagger** - Defaults to `/docs/swagger`.
* **Redoc** - Defaults to `/docs/redoc`.
* **Stoplight** - Defaults to `/docs/elements`.
* **Rapidoc** - `/docs/rapidoc`.

!!! Tip
    See the [OpenAPIConfig](./configurations/openapi/config.md) for more details how to take
    advantage of the defaults provided and how to change them.

## The OpenAPIConfig

The [OpenAPIConfig](./configurations/openapi/config.md) configuration explains in more detail
what and how to use it.

### How to use it

There are many things you can do with the OpenAPI, from simple calls to [authentication](#authentication-in-documentation)
using the docs.

Let us assume we have some apis for a `user` that will handle simple CRUD that belongs to a `blog`
project.

!!! Note
    We will not be dwelling on the technicalities of the database models but for this example
    it was used the [Edgy](./databases/edgy/motivation.md) contrib from Esmerald as it speeds
    up the development.

The APIs look like this:

```python
{!> ../../../docs_src/openapi/apis.py !}
```

The `daos` and `schemas` are simply placed in different files but you get the gist of it.

!!! Tip
    If you are not familiar with the DAO, have a look at the [official explanation](./protocols.md#dao)
    and how you can also use it.

Now it is time to see how it would look like using the official documentation.

#### Swagger

Accessing the default `/docs/swagger`, you should be able to see something like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696587523/esmerald/openapi/swagger_izvbrm.png" title="Swagger" />

And expanding one of the APIs:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696587617/esmerald/openapi/swagger-expand_v3wjlh.png" title="Swagger" />

Including the normal responses:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696587708/esmerald/openapi/details_jin7yr.png" title="Swagger" />

#### Redoc

What if you prefer redoc instead? Well, you can simply access the `/docs/redoc` and you should be
able to see something like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696587859/esmerald/openapi/redoc_sp7t4f.png" title="ReDoc" />

#### Stoplight

Esmerald also offers the Stoplight elements documentation. Accessing `/docs/elements` you should
be able to see something like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696588103/esmerald/openapi/stoplight_hjasoe.png" title="Stoplight" />

## Authentication in documentation

Now this is where the things get interesting. There are cases where the majority of your APIs will
be behind some sort of authentication and permission system and to access the data of those APIs
and **test them directly in your docs is a must**.

Esmerald comes with a pre-defined set of utilities that you can simply add you your APIs and enable
the authentication via documentation.

The `security` attribute is what Esmerald looks for when generating the docs for you and there
is where you can pass the definitions needed.

### Supported authorizations

* `HTTPBasic` - For basic authentication.
* `HTTPBearer` - For the `Authorization` of a `HTTPBearer` token. Example: `JWT` token authentication.
* `HTTPDigest` - For digest.
* `APIKeyInCookie` - For any key passed in a `cookie` with a spefific `name`.
* `APIKeyInHeader` - For any key passed in a `header` with a spefific `name`.
* `APIKeyInQuery` - For any key passed in a `query` with a spefific `name`.
* `OAuth2` - For OAuth2 authentication.
* `OpenIdConnect` - OpenIdConnect authorization.
dasda
How to import them:

```python
from esmerald.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery
from esmerald.security.http import HTTPBasic, HTTPBearer, HTTPDigest
from esmerald.security.oauth2 import OAuth2
from esmerald.security.open_id import OpenIdConnect
```

### HTTPBase

Every [supported authorization](#supported-authorizations) has the same `HTTPBase` which means
if you want to build your own custom object, you can simply inherit from it and develop it.

```python
from esmerald.security import HTTPBase
```

#### Parameters

Every [supported authorization](#supported-authorizations) has in common the following parameters:

* **type_** - The type of security scheme. Literal `apiKey`, `http`, `mutualTLS`, `oauth2` or `openIdConnect`.
* **scheme_name** (Optional) - The name for the scheme to be shown in the docs.

    <sup>Default: `__class__.__name__`</sup>

* **scheme** - The name of the HTTP Authorization scheme to be used in the
[Authorization header as defined in RFC7235](https://tools.ietf.org/html/rfc7235#section-5.1).
Example: `Authorization`.
* **scheme_name** (Optional) - The name of the header, query or cookie parameter to be used. This is should be used when using `APIKeyInCookie`, `APIKeyInHeader` or `APIKeyInQuery`.
* **description** (Optional) - A description for the security scheme.

### How to use it

Now that we are more acquainted with the [supported authorization](#supported-authorizations), let
us see how you could use them.

Let us use the following API as example from before.

```python
from typing import List

from esmerald import Request, get
from esmerald.core.datastructures import OpenAPIResponse

from .daos import UserDAO
from .schemas import Error, UserOut


@get(
    "/users",
    tags=["User"],
    description="List of all the users in the system",
    summary="Lists all users",
    responses={
        200: OpenAPIResponse(model=[UserOut]),
        400: OpenAPIResponse(model=Error, description="Bad response"),
    },
)
async def users(request: Request) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    users = UserDAO()
    return await users.get_all()
```

#### HTTPBasic

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/basic/basic_inst.py !}
```

#### HTTPBearer

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/bearer/basic_inst.py !}
```

#### HTTPDigest

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/digest/basic_inst.py !}
```

#### APIKeyInHeader

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/api_header/basic_inst.py !}
```

This now **should be the way** of declaring it there the name is `X_TOKEN_API` and this will
automatically added in your API calls that declare it.

#### APIKeyInCookie

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/api_cookie/basic_inst.py !}
```

This now **should be the way** of declaring it there the name is `X_COOKIE_API` and this will
automatically added in your API calls that declare it.

#### APIKeyInQuery

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/api_query/basic_inst.py !}
```

This now **should be the way** of declaring it there the name is `X_QUERY_API` and this will
automatically added in your API calls that declare it by adding the `?X_QUERY_API=<VALUE>`.

#### OAuth2

Now this is an extremely complex and dedicated flow. Esmerald provides [detailed explanations and examples](./security/index.md)
in its own security section, including how to use it in the OpenAPI documentation.

#### OpenIdConnect

The `openIdConnect` requires you to specify a `openIdConnectUrl` parameter.

* **openIdConnectUrl** - OpenId Connect URL to discover OAuth2 configuration values.
This MUST be in the form of a URL. The OpenID Connect standard requires the use of TLS.

**As an instance in case you need to pass extra parameters.**

```python
{!> ../../../docs_src/openapi/openid_connect/basic_inst.py !}
```

### Combine them all

Is it possible to have more than one type in the APIs? **Of course!**.

```python
{!> ../../../docs_src/openapi/all.py !}
```

## Check the documentation

With all the authentication methods added to your APIs you can now check the docs for something
like this:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696593769/esmerald/openapi/auth_button_knsd2s.png" title="Authorize" />

The `Autorize` will show and you can simply use whatever authentication method you decided to
have.

Let us see how it would look like if we have `APIKeyInHeader`, `APIKeyInCookie` and `APIKeyInQuery`.

```python
{!> ../../../docs_src/openapi/simple.py !}
```

You should see something like this when `Authorize` is called.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1696595126/esmerald/openapi/auths_idjctb.png" title="Authorize" />

Did you notice the `name` specified in each authorization object? Cool, right?.

## Levels

Like everything in Esmerald, you can specify the security on each [level of the application](./application/levels.md).
Which means, you don't need to repeat yourself if for instance, all APIs of a given [Include](./routing/routes.md#include)
require a [HTTPBearer](#httpbearer) token or any other.
