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

### Parameters

All the parameters and defaults are available in the [View Reference](../references/routing/view.md).

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
[WebSocket handlers](./handlers.md#websocket-handler)

```python title='app.py' hl_lines="15 19 26"
{!> ../docs_src/routing/handlers/apiviews/mix.py !}
```

## Constraints

When declaring an APIView and registering the route, both [Gateway](./routes.md#gateway) and
[WebSocketGateway](./routes.md#websocketgateway) allow to be used for this purpose but one has a limitation compared
to the other.

* **Gateway** - Allows the APIView to have all the available handlers (`get`, `put`, `post`...) including `websocket`.
* **WebSocketGateway** - Allows **only** to have `websockets`.

## Generics

Esmerald also offers some generics when it comes to build APIs. For example, the [APIView](#apiview)
allows the creation of apis where the function name can be whatever you desire like `create_users`,
`get_items`, `update_profile`, etc...

**Generics in Esmerald are more restrict**.

So what does that mean? Means **you can only perform operations where the function name coincides with the http verb**.
For example, `get`, `put`, `post` etc...

If you attempt to create a function where the name differs from a http verb,
an `ImproperlyConfigured` exception is raised **unless the `extra_allowed` is declared**.

The available http verbs are:

* `GET`
* `POST`
* `PUT`
* `PATCH`
* `DELETE`
* `HEAD`
* `OPTIONS`
* `TRACE`

Basically the same availability as the [handlers](./handlers.md).

### Important

The generics **enforce** the name matching of the functions with the handlers. That means, if
you use a `ReadAPIView` that only allows the `get` and you use the wrong [handlers](./handlers.md)
on the top of it, for example a [post](./handlers.md#post), an `ImproperlyConfigured` exception
will be raised.

Let us see what this means.

```python hl_lines="13-14"
{!> ../docs_src/routing/generics/important.py !}
```

As you can see, the handler `post()` does not match the function name `get`. **It should always match**.

An easy way of knowing this is simple, when it comes to the available http verbs, the function name
**should always match the handler**.

Are there any exception? Yes but not for these specific cases, the exceptions are called
[extra_allowed](#extra_allowed) but more details about this later on.

### SimpleAPIView

This is the base of all generics, subclassing from this class will allow you to perform all the
available http verbs without any restriction.

This is how you can import.

```python
from esmerald import SimpleAPIView
```

#### Example

```python
{!> ../docs_src/routing/generics/simple_api_view.py !}
```

### ReadAPIView

Allows the `GET` verb to be used.

This is how you can import.

```python
from esmerald.routing.apis.generics import ReadAPIView
```

#### Example

```python
{!> ../docs_src/routing/generics/read_api_view.py !}
```

### CreateAPIView

Allows the `POST`, `PUT`, `PATCH` verbs to be used.

This is how you can import.

```python
from esmerald.routing.apis.generics import CreateAPIView
```

#### Example

```python
{!> ../docs_src/routing/generics/create_api_view.py !}
```

### DeleteAPIView

Allows the `DELETE` verb to be used.

This is how you can import.

```python
from esmerald.routing.apis.generics import DeleteAPIView
```

#### Example

```python
{!> ../docs_src/routing/generics/delete_api_view.py !}
```

### Combining all in one

What if you want to combine them all? Of course you also can.

```python
{!> ../docs_src/routing/generics/combine.py !}
```

**Combining them all is the same as using the [SimpleAPIView](#simpleapiview)**.

### ListAPIView

This is a *nice to have* type of generic. In principle, **all the functions must return lists or None**
of any kind.

This generic **enforces the return annotations to always be lists or None**.

Allows all the verbs be used.

This is how you can import.

```python
from esmerald.routing.apis.generics import ListAPIView
```

#### Example

```python hl_lines="9 13 17 21"
{!> ../docs_src/routing/generics/list_api.py !}
```

This is another generic that follows the same rules of the [SimpleAPIView](#simpleapiview), which
means, if you want to add `extra` functions such as a `read_item()` or anything else, you must
follow the [extra allowed](#extra_allowed) principle.

```python hl_lines="8 23"
{!> ../docs_src/routing/generics/list_api_extra.py !}
```

### extra_allowed

All the generics subclass the [SimpleAPIView](#simpleapiview) as mentioned before and that superclass
uses the `http_allowed_methods` to verify which methods are allowed or not to be passed inside
the API object but also check if there is any `extra_allowed` list with any extra functions you
would like the view to deliver.

This means that if you want to add a `read_item()` function to any of the
generics you also do it easily.

```python hl_lines="13 28"
{!> ../docs_src/routing/generics/allowed.py !}
```

As you can see, to make it happen you would need to declare the function name inside the
`extra_allowed` to make sure that an `ImproperlyConfigured` is not raised.

## What to choose

All the available objects from the [APIView](#apiview) to the [SimpleAPIView](#simpleapiview) and
generics can do whatever you want and need so what and how to choose the right one for you?

Well, like everything, it will depend of what you want to achieve. For example, if you do not care
or do not want to be bothered with `http_allowed_methods` and want to go without restrictions,
then the [APIView](#apiview) is the right choice for you.

On the other hand, if you feel like restricting youself or even during development you might want
to restrict some actions on the fly, so maybe you can opt for choosing the [SimpleAPIView](#simpleapiview)
or any of the generics.

Your take!
