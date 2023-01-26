# Responses

Like every application, there are many different responses that can be used for different use cases and scenarios.

Esmerald having `Starlette` under the hood also means that all available responses from it simply just work.

You simply just need to decide which type of response your function will have and let `Esmerald` take care of the rest.

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

### JSON

The classic JSON response for 99% of the responses used nowaday. The `JSON` returns a
`JSONResponse`.

```python
{!> ../docs_src/responses/json.py !}
```

#### JSONResponse

You can always use directly the `JSONResponse` from Starlette without using the Esmerald wrapper.

```python
from starlette.responses import JSONResponse as JSONResponse
```

or alternatively

```python
from esmerald.responses import JSONResponse
```

### OrJSON

Super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/orjson.py !}
```

!!! Check
    More details about the ORJSOM can be [found here](https://github.com/ijl/orjson).

#### ORJSONResponse

You can always use directly the `ORJSONResponse` from Esmerald without using the wrapper.

```python
from esmerald.responses import ORJSONResponse
```

### UJSON

Another super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/ujson.py !}
```

!!! Check
    More details about the UJSON can be [found here](https://github.com/ultrajson/ultrajson).
    For JSONResponse the way of doing it the same as ORJSONResponse and UJSONResponse.

#### UJSONResponse

You can always use directly the `UJSONResponse` from Esmerald without using the wrapper.

```python
from esmerald.responses import UJSONResponse
```

### Template

As the name suggests, it is the response used to render HTML templates.

This response returns a `TemplateResponse`.

```python
{!> ../docs_src/responses/template.py !}
```

**Parameters**:

* **name** - Template name/location. E.g.: `accounts/list.html`.
* **context** - The dict context to be sent to the template.

### Redirect

As the name indicates, it is the response used to redirect to another endpoint/path.

This response returns a `ResponseRedirect`.

```python
{!> ../docs_src/responses/redirect.py !}
```

**Parameters**:

* **path** - The url path to redirect.

### File

The File response sends a file. This response returns a `FileResponse`.

```python
{!> ../docs_src/responses/file.py !}
```

**Parameters**:

* **path** - The path to the file to download.
* **filename** - The name of the file to be added to the `Content-Disposition` attachment.

### Stream

The Stream response uses the `StreamResponse`.

```python
{!> ../docs_src/responses/stream.py !}
```

**Parameters**:

* **iterator** - Any iterable function.

## Important notes

[Template](#template), [Redirect](#redirect), [File](#file) and [Stream](#stream) are wrappers
around the Starlette `TemplateResponse`, `RedirectResponse`, `FileResponse` and `StreamResponse`.

Those responses are also possible to be used directly without the need of using the wrapper.

The wrappers, like Starlette, also accept the classic parameters such as `headers` and `cookies`.

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

This is a special attribute that is used for OpenAPI spec purposes and can be created and added to a specific handler.

```python
from typing import Union

from esmerald import post
from esmerald.openapi.datastructures import ResponseSpecification
from pydantic import BaseModel


class ItemOut(BaseModel):
    sku: str
    description: str


@post(path='/create', summary="Creates an item", responses={200: ResponseSpecification(model=TaskIn, description=...)})
async def create() -> Union[None, ItemOut]:
    ...
```

This will add an extra response description and details to your OpenAPI spec handler definition.

## Other responses

There are other responses you can have that does not necessessarily have to be the ones provided here. Every case is
unique and you might want to return directly a `string`, a `dict`, an `integer`, a `list` or whatever you want.

```python
{!> ../docs_src/responses/others.py !}
```
