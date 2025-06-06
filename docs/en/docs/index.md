---
hide:
  - navigation
---

# Esmerald

<p align="center">
  <a href="https://esmerald.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1673619342/esmerald/img/logo-gr_z1ot8o.png" alt='Esmerald'></a>
</p>

<p align="center">
    <em>🚀 Highly scalable, performant, easy to learn, easy to code and for every application. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/esmerald/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/esmerald/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/esmerald" target="_blank">
    <img src="https://img.shields.io/pypi/v/esmerald?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/esmerald" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/esmerald.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: [https://esmerald.dev](https://www.esmerald.dev) 📚

**Source Code**: [https://github.com/dymmond/esmerald](https://github.com/dymmond/esmerald)

---

Esmerald is a modern, powerful, flexible, high performant web framework designed to build not only APIs
but also full scalable applications from the smallest to enterprise level.

Esmerald is designed to build with Python 3.10+ based on standard python type hints and on the top of
the heavily known [Lilya](https://github.com/dymmond/lilya) and [Pydantic](https://github.com/samuelcolvin/pydantic)/[msgspec](https://jcristharif.com/msgspec/).

!!! Success
    **The official supported version is always the latest released**.

## Motivation

There are great frameworks out there like FastAPI, Flama, Flask, Django... All of them solving majority
of the current day-to-day problems of 99% of the applications but leaving the 1% that is usually around structure
and design/business without to much to do.

Esmerald got the inspiration from those great frameworks out there and was built with all the known amazing
features but with business in mind as well. Starlite, for example, at the very beginning, gave the inspiration for
the transformers and for the Signature models, something very useful that helped Esmerald integerating with pydantic.
FastAPI gave the inspiration for API designing, Django for the permissions, Flask for the simplicity, NestJS for the
controllers and the list goes on.

For a job to be done properly, usually it is never done alone and there is always a driver and inspiration to it.

## Requirements

* Python 3.10+

Esmerald wouldn't be possible without at least these two:

* <a href="https://lilya.dev/" class="external-link" target="_blank">Lilya</a>
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Installation

```shell
$ pip install esmerald
```

An ASGI server is also needed to run in production, we recommend [Uvicorn](https://www.uvicorn.org) but it is entirely
up to you.

```shell
$ pip install uvicorn
```

**Support for the internal scheduler**:

```shell
$ pip install esmerald[schedulers]
```

**Support for the jwt used internally by Esmerald**:

```shell
$ pip install esmerald[jwt]
```

**If you want to use the esmerald testing client**:

```shell
$ pip install esmerald[test]
```

**If you want to use the esmerald shell**:

More [details](./directives/shell.md) about this topic [in the docs](./directives/shell.md)

```shell
$ pip install esmerald[ipython] # default shell
$ pip install esmerald[ptpython] # ptpython shell
```

### Start a project using directives

!!! Warning
    This is for more advanced users that are already comfortable with Esmerald (or Python in general)
    or feel like it is not a problem using these directives. If you do not feel comfortable yet to use this,
    please continue reading the documentation and learning more about Esmerald.

If you wish to start an Esmerald project with a simple suggested structure.

```shell
esmerald createproject <YOUR-PROJECT-NAME> --simple
```

This will generate a scaffold for your project with some pre-defined files in a simple fashion with a simple ready to
go Esmerald application.

This will also generate a file for the tests using the EsmeraldTestClient, so make sure you run:

```shell
$ pip install esmerald[test]
```

Or you can skip this step if you don't want to use the EsmeraldTestClient.

You can find [more information](./directives/directives.md) about this directive and how to use it with a detailed
example.

!!! Warning
    Running this [directive](./directives/directives.md) will generate only the scaffold of the project
    but some additional information is still needed to start the project. This only provides a structure of
    files that can be used to start an Esmerald application but **it is not mandatory**.

## Key Features

* **Fluid and Fast**: Thanks to Lilya and Pydantic/msgpec.
* **Fast to develop**: Thanks to the simplicity of design, the development times can be reduced exponentially.
* **Intuitive**: If you are used to the other frameworks, Esmerald is a no brainer to develop.
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
* **Pluggables**: Create plugins for Esmerald and hook them into any application and/or
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

Esmerald uses Lilya under the hood. The reason behind this decison comes with the fact that performance is there
and no issues with routing.

Once the application is up, all the routes are mounted and therefore the url paths are defined.
Esmerald encourages standard practices and design in mind which means that any application, big or small,
custom or enterprise, fits within Esmerald ecosystem without scalability issues.

## Quickstart

To quickly start with Esmerald, you can just do this. Using `uvicorn` as example.

```python
#!/usr/bin/env python
import uvicorn

from esmerald import Esmerald, Gateway, JSONResponse, Request, get


@get()
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald"})


@get()
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


@get()
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


app = Esmerald(
    routes=[
        Gateway("/esmerald", handler=welcome),
        Gateway("/esmerald/{user}", handler=user),
        Gateway("/esmerald/in-request/{user}", handler=user_in_request),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

Then you can access the endpoints.

### Using Esmerald as a decorator

To quickly start with Esmerald you can also use it as decorator, you can just do this. Using `uvicorn` as example.

```python
#!/usr/bin/env python
import uvicorn

from esmerald import Esmerald, JSONResponse, Request


app = Esmerald()


@app.get("/esmerald")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Esmerald"})


@app.get("/esmerald/{user}")
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


@app.get("/esmerald/in-request/{user}")
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Esmerald, {user}"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

## Settings

Like every other framework, when starting an application, a lot of [settings](./application/settings.md) can/need to be
passed to the main object and this can be very dauting and ugly to maintain and see.

Esmerald comes with the
[settings](./application/settings.md) in mind. A set of defaults that can be overridden by your very own settings
module but not limited to it, as you can still use the classic approach of passing everything into a
Esmerald instance directly when instantiating.

**Example of classic approach**:

```python
from example import ApplicationObjectExample

# ExampleObject is an instance of another application
# and it serves only for example

app = ApplicationObjectExample(setting_one=..., setting_two=..., setting_three=...)

```

Inspired by the great [Django](https://www.djangoproject.com/) and using pydantic, Esmerald has a default object
ready to be used out-of-the-box.

**Esmerald**:

```python
from esmerald import Esmerald

app = Esmerald()

```

And that's it! **All the default settings are loaded by default**! Why? Because **the application looks for a
`ESMERALD_SETTINGS_MODULE` environment variable to startup** and if not found, defaults to the application
global settings. This is simple of course but can you override inside the object as well? Yes, absolutely.

```python
from esmerald import Esmerald


app = Esmerald(app_name='My App', title='My title')

```

Same as the classics.

Let's talk [Esmerald settings module](#esmerald-settings-module).

### Esmerald Settings Module

This is the way Esmerald defaults the values. When starting an application, the system looks for a
`ESMERALD_SETTINGS_MODULE` environment variable. If no variable is supplied then the system will default to
`EsmeraldSettings` settings and start.

### Custom Settings

Separation of settings by enviromment is a must have these days and starting with default of Esmerald will not be
enough for any application.

The settings are pydantic standard settings and therefore compatible with Esmerald.
The system brings some defaults that can be used out-of-the-box, but it is not mandatory to be used.
The environment defaults to **production**.

```python
from esmerald import EsmeraldSettings
from esmerald.conf.enums import EnvironmentType


class Development(EsmeraldSettings):
    app_name: str = 'My app in dev'
    environment: str = EnvironmentType.DEVELOPMENT

```

**Load the settings into your Esmerald application**:

Assuming your Esmerald app is inside an `src/app.py`.

=== "MacOS & Linux"

    ```console
    ESMERALD_SETTINGS_MODULE='myapp.settings.Development' python -m src.app.py
    ```

=== "Windows"

    ```console
    $env:ESMERALD_SETTINGS_MODULE="myapp.settings.Development"; python -m src.app.py
    ```

## Gateway, WebSocketGateway and Include

Lilya offers the 'Path' classes for simple path assignments but this is also very limiting if something more
complex in mind. Esmerald extends that functionality and adds some `flair` and levels up by having the
[Gateway](./routing/routes.md#gateway), [WebSocketGateway](./routing/routes.md#websocketgateway)
and [Include](./routing/routes.md#include).

Those are special objects that allow all the magic of Esmerald to happen.

**For a classic, direct, one file single approach**:

=== "In a nutshell"

    ```python title='src/app.py'
    from esmerald import Esmerald, Gateway, JSONResponse, Request, Websocket, WebSocketGateway, get, status


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


    app = Esmerald(routes=[
        Gateway(handler=home),
        Gateway(handler=another),
        WebSocketGateway(handler=world_socket),
    ])

    ```

## Design in mind

Good design is always encouraged and Esmerald allows complex routing on any [level](./application/levels.md).

### The handlers (controllers)

```python title="src/myapp/accounts/controllers.py"
{!> ../../../docs_src/routing/routes/include/controllers.py!}
```

If a `path` is not provided, defaults to `/`.

### The gateways (urls)

```python title="myapp/accounts/urls.py" hl_lines="5-9"
from esmerald import Gateway, WebSocketGateway
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

## Include and Esmerald

The `Include` can be very helpful mostly when the goal is to avoid a lot of imports and massive list
of objects to be passed into one single object. This can be particulary useful to make a Esmerald instance.

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
    ESMERALD_SETTINGS_MODULE=myapp.AppSettings uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:ESMERALD_SETTINGS_MODULE="myapp.AppSettings"; uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

## OpenAPI documentation

Esmerald also comes with OpenAPI docs integrated. For those used to that, this is roughly the same and to make it
happen, there were inspirations that helped Esmerald getting there fast.

Esmerald starts automatically the OpenAPI documentation by injecting the OpenAPIConfig default from
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

This is just a very high-level demonstration of how to start quickly and what Esmerald can do.
There are plenty more things you can do with Esmerald. Enjoy! 😊

## Sponsors

Currently there are no sponsors of Esmerald, but you can financially help and support the author though
[GitHub sponsors](https://github.com/sponsors/tarsil) and become a **Special one** or a **Legend**.

### Powered by

Worth mentioning who is helping us.

**JetBrains**

[![JetBrains logo.](https://resources.jetbrains.com/storage/products/company/brand/logos/jetbrains.svg)](https://jb.gg/OpenSourceSupport)

[edgy_orm]: ./databases/edgy/motivation.md
[mongoz_odm]: ./databases/mongoz/motivation.md
