# Handlers

Handlers are part of the core of what makes `Esmerald` and they are needed to build the APIs and the routing
of the application.

They provide a set of available parameters like `status_code`, `response_class`, `include_in_schema` and many others.

## HTTP handlers

There different http handlers representing the different
<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods" target="_blank">HTTP Methods</a> available
and special one for special circumstances.

!!! warning
    In every HTTP handler ([get](#get), [post](#post), [put](#put), [patch](#patch), [delete](#delete) and [route](#route))
    if a `path` is not provided, it will default to `/`.

### GET

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/get.py !}
```

**Default status code**: `200`

### POST

```python hl_lines="11 17"
{!> ../docs_src/routing/handlers/post.py !}
```

**Default status code**: `201`

### PUT

```python hl_lines="4 9"
{!> ../docs_src/routing/handlers/put.py !}
```

**Default status code**: `200`

### PATCH

```python hl_lines="4 9"
{!> ../docs_src/routing/handlers/patch.py !}
```

**Default status code**: `200`

### DELETE

```python hl_lines="4 10"
{!> ../docs_src/routing/handlers/delete.py !}
```

**Default status code**: `204`

### Route

```python hl_lines="4 9 14 19"
{!> ../docs_src/routing/handlers/route.py !}
```

**Default status code**: `200`

`@route` is a special handler because it is designed to allow more than one `HTTP` handler in one go.

Sometimes you might want to have one [Gateway](./routes.md#gateway) that allows more than one HTTP operation but
writting two different functions with roughly the same logic can be avoided by using this special handler.

Example:

```python hl_lines="4"
{!> ../docs_src/routing/handlers/route_example1.py !}
```

There are also three more **unique** and exotic ones:

### HEAD

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/head.py !}
```

**Default status code**: `200`

### OPTIONS

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/options.py !}
```

**Default status code**: `200`

### TRACE

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/trace.py !}
```

**Default status code**: `200`

**Parameters**:

* **path** - The path for the handler. The path is then joined with the [Gateway](./routes.md#gateway) path.

    <sup>Default: `/`</sup>

* **summary** - The sumamry of the handler. Used for OpenAPI docs.
* **description** - Description of the handler. Used for OpenAPI docs.
* **content_media_type** - Content media type. Used for OpenAPI specification
* **content_encoding** - Content encoding. Used for OpenAPI specification
* **status_code** - Status code used for the response.

    <sup>GET - `200`</sup><br />
    <sup>POST - `201`</sup><br />
    <sup>PUT - `200`</sup><br />
    <sup>PATCH - `200`</sup><br />
    <sup>DELETE - `204`</sup><br />
    <sup>Route - `200`</sup>
    <sup>HEAD - `200`</sup>
    <sup>OPTIONS - `200`</sup>
    <sup>TRACE - `200`</sup>

* **include_in_schema** - If handler should be included in the OpenAPI schema.
* **background** - An instance of `BackgroundTask`. Check [backgoround tasks](../background-tasks.md) for more insights.
* **media_type** - The content type of the response.
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
* **deprecated** - Boolean flag for deprecation. Used for OpenAPI.
* **security** - Security definition of the application. Used for OpenAPI.
* **operation_id** - Internal unique identifier of the handler. Used for OpenAPI.
* **response_description** - Description of the response. Used for OpenAPI.
* **responses** - The available responses of the handler. Used for OpenAPI. [Check for more details](../responses.md#openapi-responses) how to use it.

## HTTP handler summary

* Handlers are used alongside [Gateway](./routes.md#gateway).
* There are `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, `TRACE` available to be used.
* There is a `route` special to handle more than one HTTP method at once.

## WebSocket handler

Websockets are different nature and widely used for applications where the communication between client and server
needs usually to be constantly opened.
<a href="https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API" target="_blank">More on websockets</a>.

!!! warning
    Due to the nature of websockets, Esmerald does a direct implementation of the WebSocket from Starlette which also
    means no `sync` functions.

### WebSocket

```python hl_lines="5 12 19 26 33"
{!> ../docs_src/routing/handlers/websocket.py !}
```

## WebSocket handler summary

* Handlers are used alongside [WebSocketGateway](./routes.md#websocketgateway).
* There is only one `websocket` handler available.

**Parameters**:

* **path** - The path for the handler. The path is then joined with the
[WebSocketGateway](./routes.md#websocketgateway) path.

    <sup>Default: `/`</sup>

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
