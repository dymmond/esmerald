# Routes

Esmerald has a simple but highly effective routing system capable of handling from simple routes to the most
complex ones.

Using  an enterprise application as example, the routing system surely won't be something simple with
20 or 40 direct routes, maybe it will have 200 or 300 routes where those are split by responsabilities,
components and packages and imported also inside complex design systems.
Esmerald handles with those cases without any kind of issues at all.

Starlette routing system alone wasn't enough to serve all the complexities and cases for all sort of
different APIs and systems so Esmerald created it's own.

## Gateway

A Gateway is an extension of the Route really but adds their own logic and handling capabilities as well as it's own
validations without compromising the core.

### Gateway and application

In simple terms, a Gateway is not a direct route but instead is a "wrapper" of a [handler](./handlers.md)
and maps that same handler with the application routing system.

**Parameters**:

* **path**: The path for the Gateway. If a path is not provided it defaults to `/`. The path provided is concatenated
with the handler's path like `/home/homepage`.
* **handler**: An instance of [handler](./handlers.md).
* **name**: The name for the Gateway. The name can be reversed by [`url_path_for()`](./router.md).
* **include_in_schema**: Boolean flag telling if it should be added to the OpenAPI docs.
* **owner**: Who `owns` the Gateway. If not specified, the application automatically it assign it. The owner is usually
a [router](./router.md) or an [Include](#include).
* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. The middlewares of a Gateway will be checked from
top-down.
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

=== "In a nutshell"

    ```python hl_lines="9"
    {!> ../docs_src/routing/routes/gateway_nutshell.py!}
    ```

## WebSocketGateway

Same principle as [Gateway](#gateway) with one particularity. Due to the nature of Starlette and websockets we
decided not to interfere (for now) with what already works and therefore the only supported websockets are `async`.

### WebSocketGateway and application

In simple terms, a WebSocketGateway is not a direct route but instead is a "wrapper" of a
[websocket handler](./handlers.md) and maps that same handler with the application routing system.

**Parameters**:

* **path**: The path for the WebSocketGateway. If a path is not provided it defaults to `/`.
* The path provided is concatenated with the handler's path like `/home/homepage`.
* **handler**: An instance of [handler](./handlers.md).
* **name**: The name for the WebSocketGateway. The name can be reversed by [`url_path_for()`](./router.md).
* **owner**: Who `owns` the WebSocketGateway. If not specified, the application automatically it assign it.
The owner is usually a [router](./router.md) or an [Include](#include).
* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. The middlewares of a WebSocketGateway will be 
checked from top-down.
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

=== "In a nutshell"

    ```python hl_lines="15"
    {!> ../docs_src/routing/routes/websocket_nutshell.py!}
    ```

## Include

Includes are unique to Esmerald, very similar to the `Mount` of Starlette but more powerful and with more control
and feature and allows:

1. Scalability without issues (thanks to Starlette).
2. Clean routing design.
3. Separation of concerns.
4. Separation of routes.
5. Redution of the level of imports needed through files.
6. Less human lead bugs.

!!! Warning
    Includes **DO NOT** take path parameters. E.g.: `Include('/{name:path}, routes=[...])`.

### Include and application

This is a very special object that allows the import of any routes from anywhere in the application.
`Include` accepts the import via `namespace` or via `routes` list but not both.

When using a `namespace`, the `Include` will look for the default `route_patterns` list in the imported
namespace (object) unless a different `pattern` is specified.

The patten only works if the imports are done via `namespace` and not via `routes` object.

**Parameters**:

* **path**: The path for the Include. If a path is not provided it defaults to `/`. The path provided is concatenated
with child nodes ([Gateway](#gateway), [WebSocketGateway](#websocketgateway) or **another Include**).
* **app**: An ASGIApp. When an ASGIApp is set, routes cannot be provided. Or one or the other but not both.
Example can be a `StaticFiles` app.
* **routes** - A list of routes to serve incoming HTTP and WebSocket requests.
A list of [Gateway](../routing/routes.md#gateway), [WebSocketGateway](../routing/routes.md#websocketgateway)
or [Include](../routing/routes.md#include).
* **name**: The name for the Gateway. The name can be reversed by [`url_path_for()`](./router.md).
* **owner**: Who `owns` the Include. If not specified, the application automatically it assign it. The owner is usually
a [router](./router.md) or another [Include](#include).
* **namespace**: The fully qualified module namespace where the file with routes is located.
Example: `example.myapp.routes`.
* **pattern**: The pattern to lookup inside a given namespace. Defaults to `route_patterns`.
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
* **include_in_schema**: Boolean flag telling if it should be added to the OpenAPI docs.

=== "Importing using namespace"

    ```python title='myapp/urls.py' hl_lines="3"
    {!> ../docs_src/routing/routes/include/with_namespace.py!}
    ```

=== "Importing using routes list"

    ```python title='src/myapp/urls.py' hl_lines="5"
    {!> ../docs_src/routing/routes/include/routes_list.py!}
    ```

#### Using a different pattern

```python title="src/myapp/accounts/views.py"
{!> ../docs_src/routing/routes/include/views.py!}
```

```python title="src/myapp/accounts/urls.py" hl_lines="5"
{!> ../docs_src/routing/routes/include/different_pattern.py!}
```

=== "Importing using namespace"

    ```python title='src/myapp/urls.py' hl_lines="3"
    {!> ../docs_src/routing/routes/include/namespace.py!}
    ```

#### Include and application instance

The `Include` can be very helpful mostly when the goal is to avoid a lot of imports and massive list
of objects to be passed into one single object. This can be particulary useful to make a clean start
Esmerald object as well.

**Example**:

```python title='src/urls.py' hl_lines="3"
{!> ../docs_src/routing/routes/include/app/urls.py!}
```

```python title='src/app.py' hl_lines="3"
{!> ../docs_src/routing/routes/include/app/app.py!}
```

## Nested Routes

WHen complexity increses and the level of routes increases as well, `Include` allows nested routes in a clean fashion.

=== "Simple Nested"

    ```python hl_lines="9"
    {!> ../docs_src/routing/routes/include/nested/simple.py!}
    ```

=== "Complex Nested Routes"

    ```python hl_lines="10-41"
    {!> ../docs_src/routing/routes/include/nested/complex.py!}
    ```

`Include` supports as many nested routes with different paths and Gateways, WebSocketGateways and Includes as you
desire to have. Once the application starts, the routes are assembled and it won't impact the performance, thanks
to Starlette.

Nested routes also allows all the functionalities on each level, from middleware, permissions and exception handlers
to dependencies.

### Application routes

!!! warning
    Be very careful when using the `Include` directly in the Esmerald(routes[]), importing without a `path` may incur
    in some routes not being properly mapped.

**Only applied to the application routes**:

If you decide to do this:

```python hl_lines="5 6"
{!> ../docs_src/routing/routes/careful/example1.py!}
```

**Be careful!**

What is actually happening?

1. Importing the `src.urls` without path, it will default to `/`.
2. Importing the `accounts.v1.urls` without path, it will default to `/`.

Because `accounts.v1.urls` was the last being imported without a path and matching the same path `/` as `src.urls`,
internally the system by the time of loading up the routes, it will **only** register the `src.urls` ignoring
completely the `accounts.v1.urls`.

**One possible solution**:

```python hl_lines="5 6"
{!> ../docs_src/routing/routes/solution1.py !}
```

The same is applied to the nested routes [nested routes](#application-routes).

Example:

```python hl_lines="5-12"
{!> ../docs_src/routing/routes/solution2.py !}
```

Another Example:

```python hl_lines="18-33"
{!> ../docs_src/routing/routes/solution3.py !}
```

The path is `/` for both `src.urls` and `accounts.v1.urls` and unique with their prefixes.

!!! Info
    If you are wondering why `Flask` in the examples then the answer is simple. **Esmerald supports the integration with
    other wsgi frameworks but more details can be [found here](../wsgi.md)**.

!!! Tip
    If you encounter a scenario where you need to have the same prefix for many paths (as per examples),
    simply create a [nested route](#nested-routes) and that's it.

!!! Check
    Remember, the route paths are registered only once and there is no "override". First in, first registered.
    This is feature came from Starlette and there is a reason why it's like this and we decided not to break it since
    it was designed to be hierarchical, from the top to bottom.

## Routes priority

The [application routes](#application-routes) in simple terms are simply prioritised. Since **Esmerald** uses
Starlette under the hood that also means that the incoming paths are matched agains each [Gateway](#gateway),
[WebSocketGateway](#websocketgateway) and [Include](#include) in order.

In cases where more than one, let's say Gateway could match an incoming path, you should ensure that more specifc
routes are listed before general cases.

Example:

```python
{!> ../docs_src/routing/routes/routes_priority.py !}
```

!!! warning
    The way the routes are assembled is very important and you always need to pay attention. **Esmerald** in a
    very high level does some sorting on the base routes of the application making sure that the routes where the **only
    path is `/`**, are the last ones being evaluated but this might be updated in the future and it doesn't
    stop you from following the [routes priority](#routes-priority) in any way from the beginning.

## Path parameters

Paths can use templating style for path components. The path params are only applied to [Gateway](#gateway) and
[WebSocketGateway](#websocketgateway) and **not applied** to [Include](#include).

```python
@get('/example')
async def customer(customer_id: Union[int, str]) -> None:
    ...


@get('/')
async def floating_point(number: float) -> None:
    ...

Gateway('/customers/{customer_id}', handler=customer)
```

By default this will capture characters up to the end of the path of the next '/' and also are joint to the path
of a handler. In the example above, it will become `/customers/{customer_id}/example`.

Converters can be used to modify what is being captured. The current available converters are the same ones used
by Starlette as well.

* `str` returns a string, and is the default.
* `int` returns a Python integer.
* `float` returns a Python float.
* `uuid` returns a Python `uuid.UUID` instance.
* `path` returna thje rest of the path, including any additional `/` characters.

As per standard, the converters are used by prefixing them with a colon:

```python
Gateway('/customers/{customer_id:int}', handler=customer)
Gateway('/floating-point/{number:float}', handler=floating_point)
Gateway('/uploaded/{rest_of_path:path}', handler=uploaded)
```

### Custom converters

If a need for a different converter that is not defined or available, you can also create your own. Using the same
example as Starlette since it works with **Esmerald**.

```python
{!> ../docs_src/routing/routes/converter_example.py !}
```

With the custom converter created you can now use it.

```python
Gateway('/sells/{date:datetime}', handler=sell)
```

!!! Info
    The request parameters are available also in the request, via `request.path_params` dictionary.

## Middleware, exception Handlers, dependencies and permissions

### Examples

The following examples are applied to [Gateway](#gateway), [WebSocketGateway](#websocketgateway)
and [Include](#include).

We will be using Gateway for it can be replaced by any of the above as it's common among them.

#### Middleware

As specified before, the [middleware](../middleware/middleware.md) of a Gateway are read from top down,
from the owner to the very handler and the same is applied to [exception handlers](../exception_handlers.md),
[dependencies](../dependencies.md) and [permissions](../permissions.md).

```python hl_lines="23 29-30"
{!> ../docs_src/routing/routes/middleware.py !}
```

The above example illustrates the various levels where a middleware can be implemented and because it follows an
ownership order, the order is:

1. Default application built-in middleware.
2. `BaseRequestLoggingMiddleware`.
3. `ExampleMiddleware`.
4. `RequestLoggingMiddlewareProtocol`.

More than one middleware can be added to each list.

#### Exception Handlers

```python hl_lines="19 28-30 33"
{!> ../docs_src/routing/routes/exception_handlers.py !}
```

The above example illustrates the various levels where the exception handlers can be implemented and follows an
ownership order where the order is:

1. Default application built-in exception handlers.
2. `EsmeraldException : http_esmerald_handler`.
3. `InternalServerError : http_internal_server_error_handler`.
4. `NotAuthorized: http_not_authorized_handler`.

More than one exception handler can be added to each mapping.

#### Dependencies

```python hl_lines="16 22 23"
{!> ../docs_src/routing/routes/dependencies.py !}
```

The above example illustrates the various levels where the dependencies can be implemented and follows an
ownership order where the order is:

1. `first : first_dependency`.
2. `second : second_dependency`.
3. `third: third_dependency`.

More than one dependency can be added to each mapping.

#### Permissions

Permissions are a must in **every** application. It's very hard to control flows of APIs only with
dependency injection as that can be very hard to maintain in the future whereas with a permission based
system, that can be done in the cleanest way possible. More on [permissions](../permissions.md) and how
to use them.

```python hl_lines="14 19 33 35"
{!> ../docs_src/routing/routes/permissions.py !}
```

The above example illustrates the various levels where the permissions can be implemented and follows an
ownership order where the order is:

1. `AllowAny`- From the application level.
2. `DenyAll`- From the Gateway.
3. `AllowAny`, `IsAdmin` - From the handlers.

More than one permission can be added to each list.
