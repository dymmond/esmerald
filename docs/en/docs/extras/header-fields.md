# Headers

Setting up headers is also something that usually happens within the scope of almost any application.

Let's assume you need to setup a header in your application. There are a few ways.

## Header

In your API you need a header to be passed onto the call to make you run some extra security validations.

```python hl_lines="12-14"
{!> ../../../docs_src/extras/headers/example1.py !}
```

The header is nothing more nothing less than pydantic `FieldInfo` with some extra things specific for the header
that extends the `Param`.

```python
from esmerald import Param

# or

from esmerald.params import Param
```

The same result can be achieved by using directly the `Param` field.

```python hl_lines="12-14"
{!> ../../../docs_src/extras/headers/example2.py !}
```

Since the `Param` is the base for the Esmerald parameters, you can use it directly with a key difference.

the `Header` expects a `value` field whereas the `Param` expects a `header` value.

If a header is defined and not sent properly when the call is made it will raise a `400` `BadRequest`.

## Response headers

This is something else entirely and it is used when you want to send a header with the response. Very easy to use
as well.

The `response_headers` is a simple python dictionary.

```python hl_lines="12"
{!> ../../../docs_src/extras/headers/example3.py !}
```

When you check the response from the api call, you should now also have a `myauth` header being sent as well with the
value `granted`.

This is how simple and effective you can manage response headers.
