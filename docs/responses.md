# Responses

Like every application, there are many different responses that can be used for different use cases and scenarios.

Esmerald having `Starlette` under the hood also means that all available responses from it simply just work.

You simply just need to decide which type of response your function will have and let `Esmerald` take care of the rest.

## Esmerald responses and the application

The available responses from `Esmerald` are:

* `Response`
* `ORJSONResponse`
* `UJSONResponse`
* `JSONResponse`
* `Template`

### Response

Classic and generic `Response` that fits almost every single use case out there. 

```python
{!> ../docs_src/responses/response.py !}
```

### ORJSONResponse

Super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/orjson.py !}
```

!!! Check
    More details about the ORJSOM can be [found here](https://github.com/ijl/orjson).

### UJSONResponse

Another super fast JSON serialization/deserialization response.

```python
{!> ../docs_src/responses/ujson.py !}
```

!!! Check
    More details about the UJSON can be [found here](https://github.com/ultrajson/ultrajson).
    For JSONResponse the way of doing it the same as ORJSONResponse and UJSONResponse.

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

**Or a unique custom response**: 

```python
{!> ../docs_src/responses/custom.py !}
```

Esmerald supports good design, structure and practices but does not force you to follow specific rules of anything
unless you want to.
