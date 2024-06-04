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

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.get).

### POST

```python hl_lines="11 17"
{!> ../docs_src/routing/handlers/post.py !}
```

**Default status code**: `201`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.post).

### PUT

```python hl_lines="4 9"
{!> ../docs_src/routing/handlers/put.py !}
```

**Default status code**: `200`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.put).

### PATCH

```python hl_lines="4 9"
{!> ../docs_src/routing/handlers/patch.py !}
```

**Default status code**: `200`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.patch).

### DELETE

```python hl_lines="4 10"
{!> ../docs_src/routing/handlers/delete.py !}
```

**Default status code**: `204`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.delete).

### Route

```python hl_lines="4 9 14 19"
{!> ../docs_src/routing/handlers/route.py !}
```

**Default status code**: `200`

`@route` is a special handler because it is designed to allow more than one `HTTP` handler in one go.

Sometimes you might want to have one [Gateway](./routes.md#gateway) that allows more than one HTTP operation but
writing two different functions with roughly the same logic can be avoided by using this special handler.

Example:

```python hl_lines="4"
{!> ../docs_src/routing/handlers/route_example1.py !}
```

There are also three more **unique** and exotic ones:

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.route).

### HEAD

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/head.py !}
```

**Default status code**: `200`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.head).

### OPTIONS

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/options.py !}
```

**Default status code**: `200`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.options).

### TRACE

```python hl_lines="4 9 14"
{!> ../docs_src/routing/handlers/trace.py !}
```

**Default status code**: `200`

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.trace).

## HTTP handler summary

* Handlers are used alongside [Gateway](./routes.md#gateway).
* There are `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, `TRACE` available to be used.
* There is a `route` special to handle more than one HTTP method at once.

## WebSocket handler

Websockets are different nature and widely used for applications where the communication between client and server
needs usually to be constantly opened.
<a href="https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API" target="_blank">More on websockets</a>.

!!! warning
    Due to the nature of websockets, Esmerald does a direct implementation of the WebSocket from Lilya which also
    means no `sync` functions.

### WebSocket

```python hl_lines="5 12 19 26 33"
{!> ../docs_src/routing/handlers/websocket.py !}
```

#### Parameters

All the parameters and defaults are available in the [Handlers Reference](../references/routing/handlers.md#esmerald.websocket).


## WebSocket handler summary

* Handlers are used alongside [WebSocketGateway](./routes.md#websocketgateway).
* There is only one `websocket` handler available.
