# Responses

Like every application, there are many different responses that can be used for different use cases and scenarios.

Esmerald having `Lilya` under the hood also means that all available responses from it simply just work.

You simply just need to decide which type of response your function will have and let `Esmerald` take care of the rest.

!!! Tip

    Esmerald automatically understands if you are typing/returning a **dataclass**,
    a **Pydantic dataclass** or a **Pydantic model** and converts
    them automatically into a [JSON response](#jsonresponse).

## Esmerald responses and the application

The available responses from `Esmerald` are:

* `Response`
* `JSON`
* `OrJSON`
* `UJSON`
* `Template`
* `Redirect`
* `File`
* `Stream`

## Important requirements

Some responses use extra dependencies, such as [UJSON](#ujson) and [OrJSON](#orjson). To use these
responses, you need to install:

```shell
$ pip install esmerald[encoders]
```

This will allow you to use the [OrJSON](#orjson) and [UJSON](#ujson) as well as the
[UJSONResponse](#ujsonresponse) and [ORJSONResponse](#orjsonresponse) in your projects.

### Response

Classic and generic `Response` that fits almost every single use case out there.

```python
{!> ../docs_src/responses/response.py !}
```

**Or a unique custom response**:

```python
{!> ../docs_src/responses/custom.py !}
```

Esmerald supports good design, structure and practices but does not force you to follow specific rules of anything
unless you want to.

## API Reference

Check out the [API Reference for Response](./references/responses/response.md) for more details.

### JSON

The classic JSON response for 99% of the responses used nowaday. The `JSON` returns a
`JSONResponse`.

```python
{!> ../docs_src/responses/json.py !}
```

## API Reference

Check out the [API Reference for JSON](./references/responses/json.md) for more details.

#### JSONResponse

You can always use directly the `JSONResponse` from Lilya without using the Esmerald wrapper.

```python
from lilya.responses import JSONResponse as JSONResponse
```

or alternatively

```python
from esmerald.responses import JSONResponse
```

## API Reference

Check out the [API Reference for JSONResponse](./references/responses/json-response.md) for more details.

### OrJSON

Super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/orjson.py !}
```

!!! Warning
    Please read the [important requirements](#important-requirements) before using this response.

!!! Check
    More details about the ORJSOM can be [found here](https://github.com/ijl/orjson).

## API Reference

Check out the [API Reference for OrJSON](./references/responses/orjson.md) for more details.

#### ORJSONResponse

You can always use directly the `ORJSONResponse` from Esmerald without using the wrapper.

```python
from esmerald.responses.encoders import ORJSONResponse
```

## API Reference

Check out the [API Reference for ORJSONResponse](./references/responses/orjson-response.md) for more details.

### UJSON

Another super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/ujson.py !}
```

!!! Warning
    Please read the [important requirements](#important-requirements) before using this response.

!!! Check
    More details about the UJSON can be [found here](https://github.com/ultrajson/ultrajson).
    For JSONResponse the way of doing it the same as ORJSONResponse and UJSONResponse.

## API Reference

Check out the [API Reference for UJSON](./references/responses/ujson.md) for more details.

#### UJSONResponse

You can always use directly the `UJSONResponse` from Esmerald without using the wrapper.

```python
from esmerald.responses.encoders import UJSONResponse
```

## API Reference

Check out the [API Reference for UJSONResponse](./references/responses/ujson-response.md) for more details.

### Template

As the name suggests, it is the response used to render HTML templates.

This response returns a `TemplateResponse`.

```python
{!> ../docs_src/responses/template.py !}
```

## API Reference

Check out the [API Reference for Template](./references/responses/template.md) for more details.

### Redirect

As the name indicates, it is the response used to redirect to another endpoint/path.

This response returns a `ResponseRedirect`.

```python
{!> ../docs_src/responses/redirect.py !}
```

## API Reference

Check out the [API Reference for Redirect](./references/responses/redirect.md) for more details.

### File

The File response sends a file. This response returns a `FileResponse`.

```python
{!> ../docs_src/responses/file.py !}
```

## API Reference

Check out the [API Reference for File](./references/responses/file.md) for more details.

### Stream

The Stream response uses the `StreamResponse`.

```python
{!> ../docs_src/responses/stream.py !}
```

## API Reference

Check out the [API Reference for Stream](./references/responses/stream.md) for more details.

## Important notes

[Template](#template), [Redirect](#redirect), [File](#file) and [Stream](#stream) are wrappers
around the Lilya `TemplateResponse`, `RedirectResponse`, `FileResponse` and `StreamResponse`.

Those responses are also possible to be used directly without the need of using the wrapper.

The wrappers, like Lilya, also accept the classic parameters such as `headers` and `cookies`.

## Response status codes

You need to be mindful when it comes to return a specific status code when using
[JSON](#json), [OrJSON](#orjson) and [UJSON](#ujson) wrappers.

Esmerald allows you to pass the status codes via [handler](./routing/handlers.md) and directly via
return of that same response but the if the handler has a `status_code` declared, the returned
`status_code` **takes precedence**.

Let us use an example to be more clear. This example is applied to `JSON`, `UJSON` and `OrJSON`.

### Status code without declaring in the handler

```python
{!> ../docs_src/responses/status_direct.py !}
```

In this example, the returned status code will be `202 Accepted` as it was declared directly in the
response and not in the handler.

### Status code declared in the handler

```python
{!> ../docs_src/responses/status_handler.py !}
```

In this example, the returned status code will also be `202 Accepted` as it was declared directly
in the handler response and not in the handler.

### Status code declared in the handler and in the return

Now what happens if we declare the status_code in both?

```python
{!> ../docs_src/responses/status_both.py !}
```

This **will return 202 Accepted** and not `201 Created` and the reason for that is because the
**return takes precedence** over the handler.

## OpenAPI Responses

This is a special attribute that is used for OpenAPI specification purposes and can be created and added to a specific handler.
You can add one or multiple different responses into your specification.

```python
from typing import Union

from esmerald import post
from esmerald.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel


class ItemOut(BaseModel):
    sku: str
    description: str


@post(path='/create', summary="Creates an item", responses={200: OpenAPIResponse(model=ItemOut, description=...)})
async def create() -> Union[None, ItemOut]:
    ...
```

This will add an extra response description and details to your OpenAPI spec handler definition.

### API Reference

Check out the [API Reference for OpenAPIResponse](./references/responses/openapi-response.md) for more details.

### Important

When adding an `OpenAPIResponse` you can also vary and override the defaults of each handler. For
example, the `@post` defaults to 201 but you might want to add a different response.

```python hl_lines="13"
from typing import Union

from esmerald import post
from esmerald.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel


class ItemOut(BaseModel):
    sku: str
    description: str


@post(path='/create', summary="Creates an item", responses={201: OpenAPIResponse(model=ItemOut, description=...)})
async def create() -> Union[None, ItemOut]:
    ...
```

You also might want to add more than just one response to the handler, for instance, a `401` or any
other.

```python hl_lines="19-20"
from typing import Union

from esmerald import post
from esmerald.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel


class ItemOut(BaseModel):
    sku: str
    description: str


class Error(BaseModel):
    detail: str
    line_number: int


@post(path='/create', summary="Creates an item", responses={
        201: OpenAPIResponse(model=ItemOut, description=...),
        401: OpenAPIResponse(model=Error, description=...),
    }
)
async def create() -> Union[None, ItemOut]:
    ...
```

### Lists

What if you want to specify in the response that you would like to have a list (array) of
returned objects?

Let us imagine we want to return a list of an item in one endpoint and a list of users in another.


```python hl_lines="19 26"
from typing import Union

from esmerald import post
from esmerald.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel, EmailStr


class ItemOut(BaseModel):
    sku: str
    description: str


class UserOut(BaseModel):
    name: str
    email: EmailStr


@get(path='/items', summary="Get all the items", responses={
        201: OpenAPIResponse(model=[ItemOut], description=...),
    }
)
async def get_items() -> Union[None, ItemOut]:
    ...

@get(path='/users', summary="Get all the users", responses={
        201: OpenAPIResponse(model=[UserOut], description=...),
    }
)
async def get_items() -> Union[None, UserOut]:
    ...
```

As you could notice, we simply added `[]` in the model to reflect a list in the OpenAPI
specification. That simple.

#### Errors

A `ValueError` is raised in the following scenarios:

* You try to pass a model than one pydantic model into a list. The OpenAPIResponse is a mere
representation of a response, so be compliant.
* You try to pass a model that is not a subclass of a Pydantic `BaseModel`.
* You try to pass a list of non Pydantic `BaseModels`.

When one of these scenarios occur, the following error will be raised.

> The representation of a list of models in OpenAPI can only be a total of one. Example: OpenAPIResponse(model=[MyModel])

## Other responses

There are other responses you can have that does not necessessarily have to be the ones provided here. Every case is
unique and you might want to return directly a `string`, a `dict`, an `integer`, a `list` or whatever you want.

```python
{!> ../docs_src/responses/others.py !}
```
### Example

Below we have a few examples of possible responses recognised by Esmerald automatically.

**Pydantic model**

```python hl_lines="13 24 27"
{!> ../docs_src/extras/form/model.py !}
```

**Pydantic dataclass**

```python hl_lines="14 25 28"
{!> ../docs_src/extras/form/pydantic_dc.py !}
```

**Python dataclass**

```python hl_lines="15 26 29"
{!> ../docs_src/extras/form/dataclass.py !}
```

**MsgSpec**

```python
{!> ../docs_src/responses/msgspec.py !}
```
