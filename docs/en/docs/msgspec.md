# MsgSpec

!!! Info
    WHen Msgspec was natively added to Ravyn in the version 2.4.0, it was beyond our wildest dreams
    what was about to come. With the introduction of the [Encoders](./encoders.md), every integration
    with external validators was simplified a lot.

    The following section is still applied but its for historical reasons since Pydantic and Msgspec
    in Ravyn are natively integration with Encoders but we leave this section as some principals
    are still applied but eventually we migh discontinue (or not) this part and you can treat msgspec as you
    normally treat with Pydantic approach.

```python
from ravyn.core.datastructures.msgspec import Struct
```

!!! Warning
    For a full integration of `Ravyn` with [OpenAPI](./openapi.md) this is **mandatory** to be
    used. Using `msgspec.Struct` for OpenAPI models will incur in errors.

    `ravyn.datastructures.msgspec.Struct` **is exactly the same** as `msgspec.Struct` but with
    extras added for [OpenAPI](./openapi.md) purposes.

## What is `msgspec`

As their documentation mention:

> msgspec is a fast serialization and validation library, with builtin support for JSON, MessagePack, YAML, and TOML.

`msgspec` and `Pydantic` are two extremely powerful libraries and both serve also different purposes
but there are a lot of people that prefer `msgspec` to Pydantic for its performance.

A good example, as per `msgspec` documentation.

```python
import msgspec

class User(msgspec.Struct):
    """A new type describing a User"""
    name: str
    groups: set[str] = set()
    email: str | None = None
```

## `msgspec` and Ravyn

Ravyn supports `msgspec` with the nuances of what the framework can offer
**without breaking any native functionality**.

So what does this mean? Well, Ravyn for [OpenAPI documentation](./openapi.md) uses internal
processes that rely on `Pydantic` and that should remain (at least for now) but also integrates
`msgspec` in a seemless way.

This means, when you implement `msgspec` structs in your code, the error handling is delegated
to the library and no Pydantic is involved, for obvious reasons, as well as the serialisation
and deserialization of the data.

### The nuances of Ravyn

This is what Ravyn can also do for you. By nuances, what Ravyn actually means is that you
**can mix `msgspec` structs within your Pydantic models but not the other way around**.

Is this useful? Depends of what you want to do. You probably won't be using this but it is there
in case you feel like playing around.

Nothing to worry about, we will be covering this in detail.

## Importing `msgspec`

As mentioned at the very top of this document, to import the `msgspec` module you will need to:

```python
from ravyn.core.datastructures.msgspec import Struct
```

Now, this can be a bit confusing, right? Why we need to import from this place instead of using
directly the `msgspec.Struct`?

Well, actually you can use directly the `msgspec.Struct` but as mentioned before, **Ravyn** uses
Pydantic for the [OpenAPI](./openapi.md) documentation and to add the [nuances](#the-nuances-of-ravyn)
we all love and therefore the `ravyn.datastructures.msgspec.Struct` is simply an extended
object that adds some Pydantic flavours for the [OpenAPI](./openapi.md).

This also means that you can declare [OpenAPIResponses](./responses.md#openapi-responses) using
`msgspec`. Pretty cool, right?

!!! Warning
    If you don't use the `ravyn.datastructures.msgspec.Struct`, it won't be possible
    to use the `msgspec` with Pydantic. At least not in a cleaner supported way.

## How to use it

### `ravyn.datastructures.msgspec.Struct`

Well, let us see how we would work with `msgspec` inside Ravyn.

In a nutshell, it is exactly the same as you would normally do if you were creating a Pydantic
base model or a datastructure to be used within your application.

```python
{!> ../../../docs_src/msgspec/nutshell.py !}
```

Simple, right? Yes and there is a lot going here.

You you might have noticed, we are importing from `ravyn.datastructures.msgspec` the `Struct`
and this is a good habit to have if you care about [OpenAPI documentation](./openapi.md) and then
we are simply declaring the `data` as the `User` of type `Struct` as the data in and as a response
the `User` as well.

The reason why we declare the `User` as a response it is just to show that `msgspec`
**can also be used as another Ravyn response**.

The rest, it is still as clean as always was in Ravyn.

Now, the cool part is when we send a payload to the API, something like this:

```shell
data = {"name": "Ravyn", "email": "esmerald@ravyn.dev"}
```

When this payload is sent, the **validations are done automatically by the `msgspec` library**
which means you can implement as many validations as you want as you would normally do while
using `msgspec`.

```python
{!> ../../../docs_src/msgspec/validations.py !}
```

And just like that, you are now using `msgspec` and all of its power within **Ravyn**.

### `msgspec.Struct`

As mentioned before, importing from `ravyn.datastructures.msgspec.Struct` should be the way
for Ravyn to use it without any issues but you can still use the normal `msgspec.Struct` as well.

```python
{!> ../../../docs_src/msgspec/no_import.py !}
```

Now this is possible and it will work as normal but **it comes with limitations**. When accessing
the [OpenAPI](./openapi.md), it will raise errors.

Again, `ravyn.datatructures.msgspec.Struct` is **exactly the same** as the `msgspec.Struct` with
extra Ravyn flavours and this means you
**will not have the problem of updating the version of `msgspec` anytime you need**.

### Nested structs

Well, this is now what you can do already with `msgspec` and not directly related with Ravyn but
for example purposes, let us see how it would look like it having a nested `Struct`.

```python
{!> ../../../docs_src/msgspec/nested.py !}
```

One possible [payload](./extras/request-data.md#the-payload-field) would be:

```json
{
    "name": "Ravyn",
    "email": "ravyn@ravyn.dev",
    "address": {
        "post_code": "90210",
        "street_address": "California"
    }
}
```

### The nuances of `Struct`

It was mentioned numerous times the use of `ravyn.datastructures.msgspec.Struct` and what it
could give you besides the obvious needed [OpenAPI](./openapi.md) documentation.

This is not the only thing. This special `datastructure` also allows you to **mix with Pydantic**
models if you want to.

Does that mean the `Struct` will be then evaluated by `Pydantic`? No, it does not.

The beauty of this system is that every `Struct`/`BaseModel` is evaluated by its own `library` which
means that if you have a `Struct` inside a `BaseModel`, the validations are done separately.

Why would you mix them if they are different? Well, in theory you wouldn't but you will never know
what people want so Ravyn offers that possibility **but not the other way around**.

Let us see how it would look like having both working side by side.

```python hl_lines="4 8 14 19"
{!> ../../../docs_src/msgspec/mixed.py !}
```

This works perfectly well and the payload is still like this:

```json
{
    "name": "Ravyn",
    "email": "ravyn@ravyn.dev",
    "address": {
        "post_code": "90210",
        "street_address": "California"
    }
}
```

The difference is that the `address` part of the payload will be evaluated by `msgspec` and the
rest by `Pydantic`.

## Responses

As mentioned before, the `Struct` of `msgspec` can also be used as `Response` of Ravyn. This
will enable the internal mechanisms to serialize/deserialize with the power of the native library
as everyone came to love.

You can see [more details](./responses.md#other-responses) about the types of responses you can use
with Ravyn.

## OpenAPI Documentation

Now this is the nice part of `msgspec`. How can you integrate `msgspec` with [OpenAPI](./openapi.md)?

Well, as mentioned before, in the same way you would normally do. You can also use
[OpenAPIResponse](./responses.md#openapi-responses) with the `Struct` as well!

Let us see the previous example again.

```python
{!> ../../../docs_src/msgspec/nutshell.py !}
```

This will generate a simple OpenAPI documentation using the `Struct`.

What if you want to create `OpenAPIResponse` objects? Well, there are also three ways:

1. [As single object](#as-a-single-object).
2. [As a list](#as-a-list).
3. [Mixing with Pydantic](#mixing-with-pydantic) (the [nuance](#the-nuances-of-esmerald)).

### As a single object

```python hl_lines="27 28"
{!> ../../../docs_src/msgspec/openapi/single.py !}
```

### As a list

```python hl_lines="21"
{!> ../../../docs_src/msgspec/openapi/list.py !}
```

### Mixing with Pydantic

```python hl_lines="27"
{!> ../../../docs_src/msgspec/openapi/mixing.py !}
```

## Notes

This is the integration with `msgspec` and Ravyn in a simple fashion where you can take advantage
of the powerful `msgspec` library and the elegance of Ravyn.

This section covers the dos and dont's of the `Struct` and once again, use:

```python
from ravyn.core.datastructures.msgspec import Struct
```

And have fun!
