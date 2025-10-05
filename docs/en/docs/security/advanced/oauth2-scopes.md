# OAuth2 Scopes

Ravyn supports OAuth2 scopes, offering a detailed permission system that adheres to the OAuth2 standard. This feature integrates seamlessly into your OpenAPI application and its API documentation.

OAuth2 scopes are widely used by major providers such as Facebook, Google, GitHub, Microsoft, and Twitter. Whenever an application allows you to "log in with" these platforms, it leverages OAuth2 with scopes to define specific permissions.

In this guide, we’ll explore how to manage authentication and authorization using OAuth2 scopes in Ravyn.

!!! Warning

    This section delves into advanced concepts, so beginners may prefer to skip it for now.

    While OAuth2 scopes aren't mandatory, they offer a structured way to handle permissions, seamlessly integrating with OpenAPI and API documentation. However, it’s crucial to enforce scopes or any other security measures directly in your code.

    In many cases, OAuth2 scopes might be excessive. Still, if your application requires them or you're eager to learn, continue reading to explore their implementation and benefits.

## OAuth2 Scopes and OpenAPI

OAuth2 defines "scopes" as a list of space-separated strings representing permissions.

In OpenAPI, you can define "security schemes" that use OAuth2 and declare scopes.

Each scope is a string (without spaces) used to specify security permissions, such as:

* `users:read` or `users:write`
* `instagram_basic` (used by Facebook/Instagram)
* `https://www.googleapis.com/auth/drive` (used by Google)

!!! Info
    In OAuth2, a "scope" is simply a string representing a specific permission. The format, such as including characters like `:` or even being a URL, is entirely implementation-specific. From the OAuth2 perspective, these are treated as plain strings without inherent meaning outside their defined context.

## Global View

We’ll quickly review the updates in the main [OAuth2 with Password, Bearer with JWT tokens](../oauth-jwt.md){.internal-link target=_blank}, now enhanced with OAuth2 scopes:

```python hl_lines="7 9 34 97 99-108 114-117 123-129"
{!> ../../../docs_src/security/advanced/app.py !}
```

Next, we’ll break these changes down step by step for better understanding.

## OAuth2 Security Scheme

First, we declare the OAuth2 security scheme with two scopes: `me` and `items`.

The `scopes` parameter is a `dict` with each scope as a key and its description as the value:

```python hl_lines="32-35"
{!> ../../../docs_src/security/advanced/app.py !}
```

These scopes will appear in the API docs when you log in/authorize, allowing you to select which scopes to grant access to: `me` and `items`.

This is similar to granting permissions when logging in with Facebook, Google, GitHub, etc:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733926056/esmerald/security/scopes_ujzsf9.png" alt="Scopes">

## JWT Token with Scopes

Next, update the token *path operation* to include the requested scopes in the response.

We continue to use `OAuth2PasswordRequestForm`, which has a `scopes` property containing the list of scopes from the request.

These scopes will be included in the JWT token returned.

!!! Danger
    To keep things simple, we directly include the received scopes in the token.

    In your application, make sure to only include scopes that the user is permitted to have.

```python hl_lines="148"
{!> ../../../docs_src/security/advanced/app.py !}
```

## Declare Scopes in Path Operations and Dependencies

To require the `items` scope for the `/users/me/items/` path operation, use `Security` from `Ravyn`. This works similarly to `Inject`, but includes a `scopes` parameter.

Pass the `get_current_user` dependency function to `Security`, along with the required scopes (in this case, `items`).

!!! Info

    You don't need to declare scopes in multiple locations.
    This example shows how **Ravyn** manages scopes defined at different levels.

```python hl_lines="97 155 159"
{!> ../../../docs_src/security/advanced/app.py !}
```

## Using `SecurityScopes`

Update the `get_current_user` dependency to use the previously created OAuth2 scheme.

Since this function does not require scopes itself, use `Inject` with `oauth2_scheme`.

Declare a `SecurityScopes` parameter, imported from `ravyn.security.scopes`.

```python hl_lines="20 97"
{!> ../../../docs_src/security/advanced/app.py !}
```

## Using the Scopes

The `scopes` parameter will be of type `SecurityScopes`.

It includes a `scopes` property, which is a list of all the scopes required by itself and any dependencies that use it as a sub-dependency. This might sound confusing, but it will be explained further below.

The `scopes` object also has a `scope_str` attribute, which is a single string containing all the scopes separated by spaces (we will use this later).

We create an `HTTPException` that can be reused (`raise`) at various points.

In this exception, we include the required scopes (if any) as a space-separated string (using `scope_str`). This string is placed in the `WWW-Authenticate` header, as specified by the OAuth2 standard.

```python hl_lines="97 99-108"
{!> ../../../docs_src/security/advanced/app.py !}
```

## Verify `username` and Data Structure

Check the `username` and extract the scopes.

Use a Pydantic model to validate the data, raising an `HTTPException` if validation fails.

Update the `TokenData` Pydantic model to include a `scopes` property.

Ensure the data structure is correct to prevent security issues.

Confirm the user exists, raising an exception if not.

```python hl_lines="55 109-117"
{!> ../../../docs_src/security/advanced/app.py !}
```

## Verify the Scopes

Check that the token includes all necessary scopes. If any required scopes are missing, raise an `HTTPException`.

```python hl_lines="123-129"
{!> ../../../docs_src/security/advanced/app.py !}
```

## More Details about `SecurityScopes`

You can use `SecurityScopes` at any point in the dependency tree.

It will always contain the scopes declared by the current `Security` dependencies and all dependants for that specific *path operation*.

Use `SecurityScopes` to verify token scopes in a central dependency function, with different scope requirements for each *path operation*.

## About Third-Party Integrations

This example demonstrates the OAuth2 "password" flow, which is ideal for logging into your own application using your frontend.

For applications where users connect through third-party providers (like Facebook, Google, GitHub), other OAuth2 flows are more appropriate.

The implicit flow is commonly used, while the authorization code flow is more secure but also more complex.

!!! Note
    Authentication providers might use different names for their flows, but they all adhere to the OAuth2 standard.
    **Ravyn** provides utilities for all OAuth2 authentication flows in `ravyn.security.oauth2`.

## Notes

These step by step guides were inspired by **FastAPI** great work of providing simple and yet effective examples for everyone to understand.

Ravyn adopts a different implementation internally but with the same purposes as any other framework to achieve that.
