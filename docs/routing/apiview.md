# APIView

This is a special object from **Esmerald** and aims to implement the so needed class based views for those who love
object oriented programming. Inspired by such great frameworks (Python, Go, JS), APIView was created to simplify
the life of those who like OOP.

## APIView class

```python
{!> ../docs_src/routing/handlers/apiviews/apiview.py !}
```

The APIView uses the Esmerald [handlers](./handlers.md) to create the "view" itself but also acts as the `parent`
of those same routes and therefore all the available parameters such as [permissions](../permissions.md),
[middlewares](../middleware/middleware.md), [exception handlers](../exception-handlers.md),
[dependencies](../dependencies.md) and almost every other parameter available in the handlers are also available
in the APIView.

**Parameters**:

* **path** - The path for the APIView.
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
* **response_class** - Custom subclass of [Response](../responses.md) to be used as application application response
class.
* **response_cookies** - List of [cookies](../datastructures.md) objects.
* **response_headers** - Mapping dictionary of [headers](../datastructures.md) objects.
* **tags** - List of tags to include in the OpenAPI schema.

## APIView routing

The routing is the same as declaring the routing for the handler with a simple particularity that you don't
need to declare handler by handler. Since everything is inside an [APIView](#apiview) 
objects the handlers will be automatically routed by **Esmerald** with the joint [path](#apiview-path) given to class.

```python title='views.py'
{!> ../docs_src/routing/handlers/apiviews/apiview.py !}
```

```python title='app.py' hl_lines="3 5"
{!> ../docs_src/routing/handlers/apiviews/routing.py !}
```

## APIView path

In the [APIView](#apiview) the `path` is a mandatory field, even if you pass only `/`. This helps maintaining the
structure of the routing cleaner and healthy.

!!! Warning
    Just because the `APIView` is a class it still follows the same rules of the
    [routing priority](./routes.md#routes-priority) as well.

## Path parameters

APIView is no different from the handlers, really. The same rules for the routing are applied for any route
[path param](./routes.md#path-parameters).

```python title='app.py' hl_lines="5 15"
{!> ../docs_src/routing/handlers/apiviews/path_params.py !}
```

## Websockets and handlers

The APIView also allows the mix of both [HTTP handlers](./handlers.md#http-handlers) and
[WebSocket handlers](./handlers#websocket-handler)

```python title='app.py' hl_lines="15 19 26"
{!> ../docs_src/routing/handlers/apiviews/mix.py !}
```

## Constraints

When declaring an APIView and registering the route, both [Gateway](./routes.md#gateway) and
[WebSocketGateway](./routes.md#websocketgateway) allow to be used for this purpose but one has a limitation compared
to the other.

* **Gateway** - Allows the APIView to have all the available handlers (`get`, `put`, `post`...) including `websocket`.
* **WebSocketGateway** - Allows **only** to have `websockets`.
