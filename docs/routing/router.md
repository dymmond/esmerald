# Router

The Router is the main object that links the whole Esmerald to the [Gateway](./routes.md#gateway),
[WebSocketGateway](./routes.md#websocketgateway) and [handlers](./handlers.md).

## Router class

The router class is composed by many attributes that are by default populated within the application but Esmerald
also allows to add extra [custom routers](#custom-router) as well but another way is to add a
[ChildEsmerald](#child-esmerald-application) app.

```python
{!> ../docs_src/routing/router/router_class.py!}
```

The main `Router` class is instantiated within the `Esmerald` application with the given routes and the application
starts.

!!! Info
    When adding another router to the application, [custom routers](#custom-router) and
    [ChildEsmerald](#child-esmerald-application) are available as a way of doing it. One is more limited than
    the other, in this case, custom routers are more limited than `ChildEsmerald`.

### Parameters

There are many parameters that can be passed into a router.

* **path**: The path for the Include. If a path is not provided it defaults to `/`. The path provided is concatenated
with child nodes ([Gateway](#gateway), [WebSocketGateway](#websocketgateway) or **another Include**).

    <sup>Default: `/`</sup>

* **app**: Any ASGI application.

    <sup>Default: `None`</sup>

* **routes** - A list of routes to serve incoming HTTP and WebSocket requests.
A list of [Gateway](../routing/routes.md#gateway), [WebSocketGateway](../routing/routes.md#websocketgateway)
or [Include](../routing/routes.md#include).

    <sup>Default: `None`</sup>

* **name**: The name of the router.

    <sup>Default: `None`</sup>

* **owner**: Who `owns` the router. If not specified, the application automatically it assign it. The owner is usually
a [router](./router.md) or an ASGIApp. E.g.: `WSGIMiddleware`, `Esmerald`, `StaticFiles`...

    <sup>Default: `/`</sup>

* **on_shutdown** - A list of callables to run on shutdown. Shutdown handler callables do not take any
arguments, and may be be either standard functions, or async functions.

    <sup>Default: `None`</sup>

* **on_startup** - A list of callables to run on startup. Startup handler callables do not take any
arguments, and may be be either standard functions, or async functions.

    <sup>Default: `None`</sup>

* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).

    <sup>Default: `[]`</sup>

* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).

    <sup>Default: `[]`</sup>

* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.

    <sup>Default: `{}`</sup>

* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

    <sup>Default: `{}`</sup>

* **response_class** - Custom subclass of [Response](../responses.md) to be used as application application response
class.

    <sup>Default: `None`</sup>

* **response_cookies** - List of [cookie](../datastructures.md) objects.

    <sup>Default: `None`</sup>

* **response_headers** - Mapping dictionary of header objects.

    <sup>Default: `None`</sup>

* **tags** - List of tags to include in the OpenAPI schema.

    <sup>Default: `[]`</sup>

!!! Warning
    The `response_class`, `response_cookies`, `response_headers`, `tags` and `include_in_schema` are not used
    when [add_route](#add_route) is used, only when using [ChildEsmerald](#child-esmerald-application) app.

## Custom Router

Let's assume there are specific **customer** submodules inside a `customers` dedicated file.
There are two way of separating the routes within the application, using [Include](./routes.md#include),
a [ChildEsmerald](#child-esmerald-application) or by creating another router. Let's focus on the latter.

```python hl_lines="28-35" title="/application/apps/routers/customers.py"
{!> ../docs_src/routing/router/customers.py!}
```

Above you create the `/application/apps/routers/customers.py` with all the information you need. It does not need
to be in one file, you can have a entirely seperate package just to manage the customer, it's up to you.

Now you need to add the new custom router into the main application.

```python hl_lines="1 6" title="/application/app.py"
{!> ../docs_src/routing/router/app.py!}
```

This simple and your router is added to the main **Esmerald** application.

## Child Esmerald Application

What is this? We call it `ChildEsmerald` but in fact is simply Esmerald but under a different name mostly for
visualisation purposes and for the sake of organisation.

!!! Check
    Using `ChildEsmerald` or `Esmerald` is exactly the same thing, it is only if you prefer to create a
    `sub application` and you prefer to use a different class instead of `Esmerald` to make it more organised.

When organising routes, using the `Router` class itself can be a bit limiting because there are certain attributes
that when used within an instance or a `Router` to be passed to [add_route](#add_route) they will not be picked up.

Example:

* `response_class`
* `response_cookies`
* `response_headers`
* `tags`
* `include_in_schema`

This is not a limitation or a bug, in fact it is intentional as we want to preserve the integrity of the application.

### How does it work

Let's use the same example used in the [custom routers](#custom-router) with the customers specific routes and rules.

```python hl_lines="28-40" title="/application/apps/routers/customers.py"
{!> ../docs_src/routing/router/childesmerald/customers.py!}
```

Since the `ChildEsmerald` is a representation of an [Esmerald](../application/applications.md) olass, we can pass
the otherwise limited parameters in the [custom router](#custom-router) and all the parameters available to
[Esmerald](../application/applications.md).

You can add as many `ChildEsmerald` as you desire, there are no limits.

**Now in the main application**:

```python hl_lines="5" title="/application/app.py"
{!> ../docs_src/routing/router/childesmerald/app.py!}
```

* **Adding nested applications**

```python hl_lines="9 13-14" title="/application/app.py"
{!> ../docs_src/routing/router/childesmerald/nested.py!}
```

The example above, it is showing that you could even add the same application within nested includes and for each
include you can add specific unique [permissions](../permissions.md), [middlewares](../middleware/middleware.md),
[exception handlers](../exception-handlers.md) and [dependencies](../dependencies.md) which are available on each
instance of the `Include`. The options are endeless.

!!! Note
    In terms of organisation, `ChildEsmerald` has a clean approach to the isolation of responsabilities and allow
    treating every individual module separately and simply adding it in to the main application
    in the form of [Include](./routes.md#include).

!!! Tip
    Treat the `ChildEsmerald` as an independent `Esmerald` instance.

!!! Check
    When adding a `ChildEsmerald` or `Esmerald` application, don't forget to add the unique path to the base
    `Include`, this way you can assure the routes are found properly.

## Utils

The `Router` object has some available functionalities that can be useful.

### add_route

```python
{!> ../docs_src/routing/router/add_route.py!}
```

#### Parameters

* **name** - Name of the route.
* **include_in_schema** - If route should be added to the OpenAPI Schema
* [handler](./handlers.md#http-handlers) - A HTTP handler.
* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

### add_websocket_route

#### Parameters

```python
{!> ../docs_src/routing/router/add_websocket_route.py!}

```

* **name** - Name of the route.
* [Websocket handler](./handlers.md#websocket-handler) - A websocket handler.
* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.
