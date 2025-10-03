# Interceptors

Interceptors are special Ravyn objects that implement the `InterceptorProtocol` via
[EsmeraldInterceptor](#esmeraldinterceptor).

## What are the interceptors

In many occasions you will find yourself needing some sort of logic that captures the request before
hitting your final API endpoint.

These can be extremely useful, for example, to capture some data
before passing to the API, for logging anything particulary useful or any other useful logic.

<img src="https://res.cloudinary.com/dymmond/image/upload/v1673451429/ravyn/resources/interceptors_tyohjr.png" alt="Interceptors" />

## Overview

Interceptors have a set of useful capabilities inspired by
<a href="https://en.wikipedia.org/wiki/Aspect-oriented_programming" target="_blank">AOP (Aspect Oriented Programming)</a>
techniques. This makes it possible to:

- Add extra logic before request
- Throw exceptions before hitting the route handler
- Extend basic the functionality
- Add extra logic to it. E.g: Caching, logging...

And whatever you might see suitable.

Ravyn **does not implement** two way method execution, meaning, interceptors are used to capture
the request but not the response.

## EsmeraldInterceptor

This is the main object that should be used to create your own interceptors. Every class **should**
derive from this object and implement the `intercept` functionality.

```python
from ravyn import EsmeraldInterceptor
```

or

```python
from ravyn.core.interceptors.interceptor import EsmeraldInterceptor
```

### Example

Let us assume you need to create one `interceptor` that will log a simple message before hitting the
[route handler](./routing/handlers.md).

We will be creating:

- A logging interceptor
- The route handler

**The logging interceptor**

```python
{!> ../../../docs_src/interceptors/logging.py !}
```

**The application with handlers and applying the interceptor**

```python hl_lines="11"
{!> ../../../docs_src/interceptors/app.py !}
```

## Custom interceptor

Is this the only way of creating an interceptor? No but **it is advised** to subclass the
[EsmeraldInterceptor](#esmeraldinterceptor) as shown above.

Let us see how it would look like the same app with a custom interceptor then.

**The logging interceptor**

```python hl_lines="7"
{!> ../../../docs_src/interceptors/custom/logging.py !}
```

**The application with handlers and applying the interceptor**

```python hl_lines="11"
{!> ../../../docs_src/interceptors/app.py !}
```

It is very similar correct? Yes but the main difference here happens within the
[EsmeraldInterceptor](#esmeraldinterceptor) as this one implements the `InterceptorProtocol` from
Ravyn and therefore makes it the right way of using it.

## Interceptors and levels

Like everything in Ravyn works in [levels](./application/levels.md), the `interceptors` are no
exception to this but has some constraints.

- The interceptors only work on [Ravyn](./application/applications.md),
[ChildRavyn](./routing/router.md#child-ravyn-application),
[Router](./routing/router.md#router),
[Gateway](./routing/routes.md#gateway),
[WebsocketGateway](./routing/routes.md#websocketgateway) and [Include](./routing/routes.md#include)
**and do not work on handlers directly**.
- When working with Ravyn and ChildRavyn, the [interceptors work in isolation](#working-in-isolation).

### Examples using levels

Let us assume we have two interceptors. One intercepts and changes the value of the
request parameter and another tries to parse a value into an `int` type.

The examples below are just that, examples and you will not be doing too much with those but
you can get the idea of it.

**RequestParamInterceptor**

```python
{!> ../../../docs_src/interceptors/request_interceptor.py !}
```

**CookieInterceptor**

```python
{!> ../../../docs_src/interceptors/cookie_interceptor.py !}
```

**The application**

The application calling both interceptors on different levels, the `app` level and the `gateway`
level.

```python hl_lines="12-13"
{!> ../../../docs_src/interceptors/app_with_levels.py !}
```

The same logic can algo be applied to [Include](./routing/routes.md#include) and
[nested Include](./routing/routes.md#nested-routes).

All of the levels described here allow to pass `interceptors`.

## Working in isolation

Every **Ravyn** and **ChildRavyn** application is considered independent, which means,
the resources can be "isolated" but Ravyn also allows the share of the resources across parent
and children.

For example, using the example from before, adding `RequestParamInterceptor` on the top of
an Ravyn app and adding the `CookieInterceptor` in the ChildRavyn will work separately.

```python hl_lines="17 22"
{!> ../../../docs_src/interceptors/child.py !}
```

The `RequestParamInterceptor` will work for the routes of the Ravyn and subsequent chilren,
the ChildRavyn, which means, you can also achieve the same result by doing this:

```python hl_lines="17"
{!> ../../../docs_src/interceptors/child_shared.py !}
```

## Interceptors and the application

To add interceptors to the main application as defaults, the way of doing it is by passing the
parameters when creating the application.

```python hl_lines="13"
{!> ../../../docs_src/interceptors/interceptors_and_app.py !}
```

## Interceptors and settings module

Like everything in Ravyn, the settings also allow to pass the interceptors instead of passing
directly when creating the Ravyn instance. A cleaner way of doing it.

**settings.py**

```python
{!> ../../../docs_src/interceptors/settings.py !}
```

**app.py**

```python
{!> ../../../docs_src/interceptors/clean_app.py !}
```

With the `settings` and the `app` created you can simply start the server and pass the newly
settings module.

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=settings.AppSettings uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="settings.AppSettings"; uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

!!! Note
    You should replace the location of the settings in the example by the one you have
    in your project. This was used as example only.

## API Reference

Check out the [API Reference for Interceptors](./references/interceptors.md) for more details.
