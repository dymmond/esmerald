---
hide:
  - navigation
---

# Ravyn

<p align="center">
  <a href="https://ravyn.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1759490296/ravyn/img/logo_pb3fis.png" alt='Ravyn'></a>
</p>

<p align="center">
    <em>🚀 Performance, type safety, and elegance. A next-generation async Python framework for APIs, microservices, and web applications. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/v/ravyn?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/ravyn.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: [https://ravyn.dev](https://www.ravyn.dev) 📚

**Source Code**: [https://github.com/dymmond/ravyn](https://github.com/dymmond/ravyn)

**The official supported version is always the latest released**.

**If you came looking for Esmerald, you are in the right place. Esmerald was rebranded to Ravyn**.

---

Ravyn is a modern, powerful, flexible, high performant web framework designed to build not only APIs
but also full scalable applications from the smallest to enterprise level.

Ravyn is designed to build with Python 3.10+ based on standard python type hints and on the top of
the heavily known [Lilya](https://github.com/dymmond/lilya) and [Pydantic](https://github.com/samuelcolvin/pydantic)/[msgspec](https://jcristharif.com/msgspec/).

!!! Success
    **The official supported version is always the latest released**.

## Motivation

There are great frameworks out there like FastAPI, Flama, Flask, Django... All of them solving majority
of the current day-to-day problems of 99% of the applications but leaving the 1% that is usually around structure
and design/business without to much to do.

Ravyn got the inspiration from those great frameworks out there and was built with all the known amazing
features but with business in mind as well. Starlite, for example, at the very beginning, gave the inspiration for
the transformers and for the Signature models, something very useful that helped Ravyn integrating with pydantic.
FastAPI gave the inspiration for API designing, Django for the permissions, Flask for the simplicity, NestJS for the
controllers and the list goes on.

For a job to be done properly, usually it is never done alone and there is always a driver and inspiration to it.

## History Behind Ravyn

Why is this happening? Is Esmerald going away? **No, absolutely not. Esmerald remains and will remain as is and will keep growing**
as it has its own use cases.

The reason for the rebranding its because the ecosystem has grown a lot and Esmerald was the first tool being created.
Since then it was released as version 3+.

This happened because of internal dependencies, and we already removed all of them but goes a bit off compared to the rest
of the ecosystem.

This is the reason for Ravyn to come into existence and to keep everything aligned with the future projects coming out.

## Requirements

* Python 3.10+

Ravyn wouldn't be possible without at least these two:

* <a href="https://lilya.dev/" class="external-link" target="_blank">Lilya</a>
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Installation

```shell
$ pip install ravyn
```

**If you want the ravyn client and all the niceties**

```shell
$ pip install ravyn[standard]
```

An ASGI server is also needed to run in production, we recommend [Uvicorn](https://www.uvicorn.org) but it is entirely
up to you.

```shell
$ pip install uvicorn
```

**Support for the internal scheduler**:

```shell
$ pip install ravyn[schedulers]
```

**Support for the jwt used internally by Ravyn**:

```shell
$ pip install ravyn[jwt]
```

**If you want to use the ravyn testing client**:

```shell
$ pip install ravyn[test]
```

**If you want to use the ravyn shell**:

More [details](./directives/shell.md) about this topic [in the docs](./directives/shell.md)

```shell
$ pip install ravyn[ipython] # default shell
$ pip install ravyn[ptpython] # ptpython shell
```

### Start a project using directives

!!! Warning
    This is for more advanced users that are already comfortable with Ravyn (or Python in general)
    or feel like it is not a problem using these directives. If you do not feel comfortable yet to use this,
    please continue reading the documentation and learning more about Ravyn.

If you wish to start an Ravyn project with a simple suggested structure.

```shell
ravyn createproject <YOUR-PROJECT-NAME> --simple
```

This will generate a scaffold for your project with some pre-defined files in a simple fashion with a simple ready to
go Ravyn application.

This will also generate a file for the tests using the RavynTestClient, so make sure you run:

```shell
$ pip install ravyn[test]
```

Or you can skip this step if you don't want to use the RavynTestClient.

You can find [more information](./directives/directives.md) about this directive and how to use it with a detailed
example.

!!! Warning
    Running this [directive](./directives/directives.md) will generate only the scaffold of the project
    but some additional information is still needed to start the project. This only provides a structure of
    files that can be used to start an Ravyn application but **it is not mandatory**.

## Key Features

* **Fluid and Fast**: Thanks to Lilya and Pydantic/msgpec.
* **Fast to develop**: Thanks to the simplicity of design, the development times can be reduced exponentially.
* **Intuitive**: If you are used to the other frameworks, Ravyn is a no brainer to develop.
* **Easy**: Developed with design in mind and easy learning.
* **Short**: With the OOP available natively there is no need for code duplication. SOLID.
* **Ready**: Get your application up and running with production-ready code.
* **OOP and Functional**: Design APIs in any desired way. OOP or Functional is available.
* **Async and Sync**: Do you prefer sync or async? You can have both.
* **Middleware**: Apply middlewares on the application level or API level.
* **Exception Handlers**: Apply exception handlers on any desired level.
* **Permissions**: Apply specific rules and permissions on each API.
* **Interceptors**: Intercept requests and add logic before reaching the endpoint.
* **Observables** - Support for observables allowing to create reactive programming within your application
* **Pluggables**: Create plugins for Ravyn and hook them into any application and/or
distribute them.
* **DAO and AsyncDAO**: Avoid database calls directly from the APIs. Use business objects instead.
* **ORM Support**: Native support for [Edgy][edgy_orm].
* **ODM Support**: Native support for [Mongoz][mongoz_odm].
* **Controller**: Class Based endpoints for your beloved OOP design.
* **JSON serialization/deserialization**: Both UJSON and ORJSON support.
* **Lifespan**: Support for the newly Lilya lifespan.
* **Dependency Injection**: Like any other great framework out there.
* **Scheduler**: Yes, that's right, we come with a scheduler for those background tasks.
* **Simplicity from settings**: Yes, we have a way to make the code even cleaner by introducing settings
based systems.
* **Encoders** - Support for custom encoders allowing compatibility with any favourity validation library: `msgspec`, `attrs`....

## Relation to Lilya and other frameworks

Ravyn uses Lilya under the hood. The reason behind this decison comes with the fact that performance is there
and no issues with routing.

Once the application is up, all the routes are mounted and therefore the url paths are defined.
Ravyn encourages standard practices and design in mind which means that any application, big or small,
custom or enterprise, fits within Ravyn ecosystem without scalability issues.

## Quickstart

To quickly start with Ravyn, you can just do this. Using `uvicorn` as example.

```python
#!/usr/bin/env python
import uvicorn

from ravyn import Ravyn, Gateway, JSONResponse, Request, get


@get()
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Ravyn"})


@get()
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


@get()
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


app = Ravyn(
    routes=[
        Gateway("/ravyn", handler=welcome),
        Gateway("/ravyn/{user}", handler=user),
        Gateway("/ravyn/in-request/{user}", handler=user_in_request),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

Then you can access the endpoints.

### Using Ravyn as a decorator

To quickly start with Ravyn you can also use it as decorator, you can just do this. Using `uvicorn` as example.

```python
#!/usr/bin/env python
import uvicorn

from ravyn import Ravyn, JSONResponse, Request

app = Ravyn()


@app.get("/ravyn")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Ravyn"})


@app.get("/ravyn/{user}")
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


@app.get("/ravyn/in-request/{user}")
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

## Settings

Like every other framework, when starting an application, a lot of [settings](./application/settings.md) can/need to be
passed to the main object and this can be very dauting and ugly to maintain and see.

Ravyn comes with the
[settings](./application/settings.md) in mind. A set of defaults that can be overridden by your very own settings
module but not limited to it, as you can still use the classic approach of passing everything into a
Ravyn instance directly when instantiating.

**Example of classic approach**:

```python
from example import ApplicationObjectExample

# ExampleObject is an instance of another application
# and it serves only for example

app = ApplicationObjectExample(setting_one=..., setting_two=..., setting_three=...)

```

Inspired by the great [Django](https://www.djangoproject.com/) and using pydantic, Ravyn has a default object
ready to be used out-of-the-box.

**Ravyn**:

```python
from ravyn import Ravyn

app = Ravyn()

```

And that's it! **All the default settings are loaded by default**! Why? Because **the application looks for a
`RAVYN_SETTINGS_MODULE` environment variable to startup** and if not found, defaults to the application
global settings. This is simple of course but can you override inside the object as well? Yes, absolutely.

```python
from ravyn import Ravyn

app = Ravyn(app_name='My App', title='My title')

```

Same as the classics.

Let's talk [Ravyn settings module](#ravyn-settings-module).

### Ravyn Settings Module

This is the way Ravyn defaults the values. When starting an application, the system looks for a
`RAVYN_SETTINGS_MODULE` environment variable. If no variable is supplied then the system will default to
`RavynSettings` settings and start.

### Custom Settings

Separation of settings by enviromment is a must have these days and starting with default of Ravyn will not be
enough for any application.

The settings are pydantic standard settings and therefore compatible with Ravyn.
The system brings some defaults that can be used out-of-the-box, but it is not mandatory to be used.
The environment defaults to **production**.

```python
from ravyn import RavynSettings
from ravyn.conf.enums import EnvironmentType


class Development(RavynSettings):
    app_name: str = 'My app in dev'
    environment: str = EnvironmentType.DEVELOPMENT

```

**Load the settings into your Ravyn application**:

Assuming your Ravyn app is inside an `src/app.py`.

=== "MacOS & Linux"

    ```console
    RAVYN_SETTINGS_MODULE='myapp.settings.Development' python -m src.app.py
    ```

=== "Windows"

    ```console
    $env:RAVYN_SETTINGS_MODULE="myapp.settings.Development"; python -m src.app.py
    ```

## Gateway, WebSocketGateway and Include

Lilya offers the 'Path' classes for simple path assignments but this is also very limiting if something more
complex in mind. Ravyn extends that functionality and adds some `flair` and levels up by having the
[Gateway](./routing/routes.md#gateway), [WebSocketGateway](./routing/routes.md#websocketgateway)
and [Include](./routing/routes.md#include).

Those are special objects that allow all the magic of Ravyn to happen.

**For a classic, direct, one file single approach**:

=== "In a nutshell"

    ```python title='src/app.py'
    from ravyn import Ravyn, Gateway, JSONResponse, Request, Websocket, WebSocketGateway, get, status


    @get(status_code=status.HTTP_200_OK)
    async def home() -> JSONResponse:
        return JSONResponse({
            "detail": "Hello world"
        })


    @get()
    async def another(request: Request) -> dict:
        return {
            "detail": "Another world!"
        }


    @websocket(path="/{path_param:str}")
    async def world_socket(socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()


    app = Ravyn(routes=[
        Gateway(handler=home),
        Gateway(handler=another),
        WebSocketGateway(handler=world_socket),
    ])

    ```

## Design in mind

Good design is always encouraged and Ravyn allows complex routing on any [level](./application/levels.md).

### The handlers (controllers)

```python title="src/myapp/accounts/controllers.py"
{!> ../../../docs_src/routing/routes/include/controllers.py!}
```

If a `path` is not provided, defaults to `/`.

### The gateways (urls)

```python title="myapp/accounts/urls.py" hl_lines="5-9"
from ravyn import Gateway, WebSocketGateway
from .controllers import home, another, world_socket, World

route_patterns = [
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]

```

If a `path` is not provided, defaults to `/`.

### The Include

This is a very special object that allows the `import` of any route from anywhere in the application.

`Include` accepts the import via `namespace` or via `routes` list but not both.

When using a `namespace`, the `Include` will look for the default `route_patterns` object list in the imported
namespace unless a different `pattern` is specified.

!!! note
    The pattern only works if the imports are done via `namespace` and not via `routes`.

=== "Importing using namespace"

    ```python title='src/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/app/urls.py!}
    ```

=== "Importing using routes"

    ```python title='src/myapp/urls.py' hl_lines="5"
    {!> ../../../docs_src/routing/routes/include/routes_list.py!}
    ```

If a `path` is not provided, defaults to `/`.

#### Using a different pattern

```python title="src/myapp/accounts/urls.py" hl_lines="5"
{!> ../../../docs_src/routing/routes/include/different_pattern.py!}
```

=== "Importing using namespace"

    ```python title='src/myapp/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/namespace.py!}
    ```

## Include and Ravyn

The `Include` can be very helpful mostly when the goal is to avoid a lot of imports and massive list
of objects to be passed into one single object. This can be particulary useful to make a Ravyn instance.

**Example**:

```python title='src/urls.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/urls.py!}
```

```python title='src/app.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/app.py!}
```

## Run the application

As mentioned before, we recommend uvicorn for production, but it is not mandatory.

**Using uvicorn**:

```shell
uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Run the application with custom settings

**Using uvicorn**:

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=myapp.AppSettings uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="myapp.AppSettings"; uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

## OpenAPI documentation

Ravyn also comes with OpenAPI docs integrated. For those used to that, this is roughly the same and to make it
happen, there were inspirations that helped Ravyn getting there fast.

Ravyn starts automatically the OpenAPI documentation by injecting the OpenAPIConfig default from
the settings and makes Swagger, ReDoc an Stoplight elements available to you out of the box.

To access the OpenAPI, simply start your local development and access:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.
* **Stoplight Elements** - `/docs/elements`.
* **Rapidoc** - `/docs/rapidoc`.

There are more details about [how to configure the OpenAPIConfig](./configurations/openapi/config.md)
within this documentation.

There is also a good explanation on how to use the [OpenAPIResponse](./responses.md#openapi-responses)
as well.

## Notes

This is just a very high-level demonstration of how to start quickly and what Ravyn can do.
There are plenty more things you can do with Ravyn. Enjoy! 😊

## Sponsors

Currently there are no sponsors of Ravyn, but you can financially help and support the author though
[GitHub sponsors](https://github.com/sponsors/tarsil) and become a **Special one** or a **Legend**.

### Powered by

Worth mentioning who is helping us.

**JetBrains**

[![JetBrains logo.](https://resources.jetbrains.com/storage/products/company/brand/logos/jetbrains.svg)](https://jb.gg/OpenSourceSupport)

[edgy_orm]: ./databases/edgy/motivation.md
[mongoz_odm]: ./databases/mongoz/motivation.md
