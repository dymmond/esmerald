# Esmerald

<p align="center">
  <a href="https://esmerald.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1673619342/esmerald/img/logo-gr_z1ot8o.png" alt='Esmerald'></a>
</p>

<p align="center">
    <em>🚀 Highly scalable, performant, easy to learn, easy to code and for every application. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/esmerald/workflows/Test%20Suite/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/esmerald/workflows/Test%20Suite/badge.svg?event=push&branch=main" alt="Test Suite">
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

**The official supported version is always the latest released**.

---

Esmerald is a modern, powerful, flexible, high performant, web framework designed to build not only APIs
but also full scalable applications from the smallest to enterprise level.

Esmerald is designed to build with python 3.8+ and based on standard python type hints. Initially
built on the top of [Starlette](https://github.com/encode/starlette) and later on moved to [Lilya](https://lilya.dev) and [Pydantic](https://github.com/samuelcolvin/pydantic)/[msgspec](https://jcristharif.com/msgspec/).

Check out the [Esmerald documentation 📚](https://esmerald.dev)

**The official supported version is always the latest released**.

## Motivation

There are great frameworks out there like FastAPI, Starlite, Flama, Flask, Django... All of them solving majority
of the current day-to-day problems of 99% of the applications but leaving the 1% that is usually around structure
and design/business without to much to do.

Esmerald got the inspiration from those great frameworks out there and was built with all the known amazing
features but with business in mind as well. Starlite, for example, gave the inspiration for the transformers and for the Signature models,
something very useful that helped Esmerald integerating with pydantic.
FastAPI gave the inspiration for API designing, Django for the permissions, Flask for the simplicity, NestJS for the
controllers and the list goes on.

For a job to be done properly, usually it is never done alone and there is always a driver and inspiration to it.

## Requirements

* python 3.8+

Esmerald wouldn't be possible without two colossals:

* <a href="https://www.lilya.dev/" class="external-link" target="_blank">Starlette</a>
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

If you want install esmerald with specifics:

**Support for template system such as jinja2 and mako**:

```shell
$ pip install esmerald[templates]
```

**Support for the internal scheduler**:

```shell
$ pip install esmerald[schedulers]
```

**Support for the jwt used internally by Esmerald**:

```shell
$ pip install esmerald[jwt]
```

**Support for ORJSON and UJSON**:

```shell
$ pip install esmerald[encoders]
```

**If you want to use the esmerald testing client**:

```shell
$ pip install esmerald[test]
```

**If you want to use the esmerald shell**:

More [details](https://esmerald.dev/directives/shell) about this topic [in the docs](https://esmerald.dev/directives/shell)

```shell
$ pip install esmerald[ipython] # default shell
$ pip install esmerald[ptpython] # ptpython shell
```

### Start a project using directives

!!! Warning
    This is for more advanced users that are already comfortable with Esmerald (or Python in general)
    or feel like it is not a problem using these directives. If you do not feel comfortable yet to use this,
    please continue reading the documentation and learning more about Esmerald.

If you wish to start an Esmerald project with a default suggested structure.

```shell
esmerald createproject <YOUR-PROJECT-NAME>
```

This will generate a scaffold for your project with some pre-defined files in a simple fashion.
This will also generate a file for the tests using the EsmeraldTestClient, so make sure you run:

```shell
$ pip install esmerald[test]
```

Or you can skip this step if you don't want to use the EsmeraldTestClient.

You can find [more information](https://esmerald.dev/management/directives) about this directive and how to
use it.

## Key Features

* **Fluid and Fast**: Thanks to Starlette and Pydantic/msgspec.
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
* **Pluggables**: Create plugins for Esmerald and hook them into any application and/or
distribute them.
* **DAO and AsyncDAO**: Avoid database calls directly from the APIs. Use business objects instead.
* **ORM Support**: Native support for [Saffier][saffier_orm] and [Edgy][edgy_orm].
* **ODM Support**: Native support for [Mongoz][mongoz_odm].
* **APIView**: Class Based endpoints for your beloved OOP design.
* **JSON serialization/deserialization**: Both UJSON and ORJON support.
* **Lifespan**: Support for the newly lifespan and on_start/on_shutdown events.
* **Scheduler**: Yes, that's right, it comes with a scheduler for those automated tasks.
* **Dependency Injection**: Like any other great framework out there.
* **Simplicity from settings**: Yes, we have a way to make the code even cleaner by introducing settings
based systems.
* **msgspec** - Support for `msgspec`.

## Relation to Starlette and other frameworks

Esmerald uses Starlette under the hood. The reason behind this decison comes with the fact that performance is there
and no issues with routing.

Once the application is up, all the routes are mounted and therefore the url paths are defined.
Esmerald encourages standard practices and design in mind which means that any application, big or small,
custom or enterprise, fits within Esmerald ecosystem without scalability issues.

## Settings

Like every other framework, when starting an application, a lot of [settings](./application/settings.md) can/need to be
passed to the main object and this can be very dauting and hugly to maintain and see.

Esmerald comes with the
[settings](./application/settings.md) in mind. A set of defaults that can be overridden by your very own settings
module but not limited to it as you can still use the classic approach of passing everything into a
Esmerald instance directly when instantiating.

**Example of classic approach**:

```python
from example import ExampleObject

# ExampleObject is an instance of another application
# and it serves only for example

app = ExampleObject(setting_one=..., setting_two=..., setting_three=...)

```

Inspired by the great [Django](https://www.djangoproject.com/) and using pydantic, Esmerald has a default object
ready to be used out-of-the-box.

**Esmerald**:

```python
from esmerald import Esmerald

app = Esmerald()

```

And that's it! All the default settings are loaded! This is simple of course but can you override
inside the object as well? Yes!

```python
from esmerald import Esmerald

app = Esmerald(app_name='My App', title='My title')

```

Same as the classics.

So how does Esmerald know about the default settings? Enters [Esmerald settings module](#esmerald-settings-module).

### Esmerald Settings Module

This is the way Esmerald defaults the values. When starting an application, the system looks for a
`ESMERALD_SETTINGS_MODULE` environment variable. If no variable is supplied then the system will default to
`EsmeraldAPISettings` settings and start.

### Custom Settings

Separation of settings by enviromment is a must have these days and starting with default of Esmerald will not be
enough for any application.

The settings are pydantic standard settings and therefore compatible with Esmerald.
The system brings some defaults that can be used out-of-the-box but it's not mandatory to be used.
The environment defaults to **production**.

```python

from esmerald import EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType

class Development(EsmeraldAPISettings):
    app_name: bool = 'My app in dev'
    environment: str = EnvironmentType.DEVELOPMENT

```

**Load the settings into your Esmerald application**:

Assuming your Esmerald app is inside an `src/app.py`.

```console

ESMERALD_SETTINGS_MODULE='myapp.settings.Development' python -m src.app.py

```

## Gateway, WebSocketGateway and Include

Starlette offers the Route classes for simple path assignments but this is also very limiting if something more
complex in mind. Esmerald extends that functionality and adds some `flair` and levels up by having the
Gateway, WebSocketGateway and Include.

Those are special objects that allow all the magic of Esmerald to happen.

For a classic, direct, one file single approach.

**In a nutshell**:

```python title='src/app.py'
from esmerald import Esmerald, get, status, Request, UJSONResponse, Gateway, WebSocketGateway, Websocket

@get(status_code=status.HTTP_200_OK)
async def home() -> UJSONResponse:
    return UJSONResponse({
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

Good design is always encouraged and Esmerald allows complex routing on any level.

### The handlers (views)

```python title="myapp/accounts/views.py"
from esmerald import get, post, put, status, websocket, APIView, Request, JSONResponse, Response, WebSocket
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    sku: str
    price: float


@put('/product/{product_id}')
def update_product(product_id: int, data: Product) -> dict:
    return {"product_id": product_id, "product_name": product.name }


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


class World(APIView):

    @get(path='/{url}')
    async def home(request: Request, url: str) -> Response:
        return Response(f"URL: {url}")

    @post(path='/{url}', status_code=status.HTTP_201_CREATED)
    async def mars(request: Request, url: str) -> JSONResponse:
        ...

    @websocket(path="/{path_param:str}")
    async def pluto(self, socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()


```

If a `path` is not provided, defaults to `/`.

### The gateways (urls)

```python title="myapp/accounts/urls.py"
from esmerald import Gateway, WebSocketGateway
from .views import home, another, world_socket, World

route_patterns = [
    Gateway(handler=update_product),
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]

```

If a `path` is not provided, defaults to `/`.

### The Include

This is a very special object that allows the import of any route from anywhere in the application.

`Include` accepts the import via `namespace` or via `routes` list but not both.

When using a `namespace`, the `Include` will look for the default `route_patterns` object list in the imported
namespace unless a different `pattern` is specified.

The pattern only works if the imports are done via `namespace` and not via `routes`.

**Importing using namespace**:

```python title='myapp/urls.py'
from esmerald import Include

route_patterns = [
    Include(namespace='myapp.accounts.urls')
]

```

**Importing using routes**:

```python title='src/myapp/urls.py'
from esmerald import Include
from myapp.accounts import urls

route_patterns = [
    Include(routes=urls.route_patterns)
]

```

If a `path` is not provided, defaults to `/`.

#### Using a different pattern

```python title="src/myapp/accounts/urls.py"
from esmerald import Gateway, WebSocketGateway
from .views import home, another, world_socket, World

my_urls = [
    Gateway(handler=update_product),
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]

```

**Importing using namespace**:

```python title='src/myapp/urls.py'
from esmerald import Include

route_patterns = [
    Include(namespace='myapp.accounts.urls', pattern='my_urls')
]

```

## Include and Esmerald

The `Include` can be very helpful mostly when the goal is to avoid a lot of imports and massive list
of objects to be passed into one single object. This can be particulary useful to make a Esmerald instance.

**Example**:

```python title='src/urls.py'
from esmerald import Include

route_patterns = [
    Include(namespace='myapp.accounts.urls', pattern='my_urls')
]

```

```python title='src/app.py'
from esmerald import Esmerald, Include

app = Esmerald(routes=[Include('src.urls')])

```

## Run the application

As mentioned before, we recomment uvicorn for production but it's not mandatory.

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

```shell
ESMERALD_SETTINGS_MODULE=myapp.AppSettings uvicorn src:app --reload

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

There are more details about [how to configure the OpenAPIConfig](https://esmerald.dev/configurations/openapi/config)
within the documentation.

There is also a good explanation on how to use the [OpenAPIResponse](https://esmerald.dev/responses#openapi-responses)
as well.

## Notes

This is just a very high-level demonstration of how to start quickly and what Esmerald can do.
There are plenty more things you can do with Esmerald. Enjoy! 😊

## Sponsors

Currently there are no sponsors of Esmerald but you can financially help and support the author though
[GitHub sponsors](https://github.com/sponsors/tarsil) and become a **Special one** or a **Legend**.

[saffier_orm]: https://esmerald.dev/databases/saffier/motivation
[edgy_orm]: https://esmerald.dev/databases/saffier/motivation
[mongoz_odm]: https://esmerald.dev/databases/mongoz/motivation
