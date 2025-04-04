# Cookies

Setting up cookies is also something that usually happens within the scope of almost any application.

Let's assume you need to setup a cookie in your application. There are a few ways.

## Cookie as a param

In your API you need a cookie to be passed onto the call to make you run some extra security validations, like `CSRF`.

```python hl_lines="12-14"
{!> ../../../docs_src/extras/cookies/example1.py !}
```

The cookie is nothing more nothing less than pydantic `FieldInfo` with some extra things specific for the cookie
that extends the `Param`.

```python
from esmerald import Param

# or

from esmerald.params import Param
```

The same result can be achieved by using directly the `Param` field.

```python hl_lines="12-14"
{!> ../../../docs_src/extras/cookies/example2.py !}
```

Since the `Param` is the base for the Esmerald parameters, you can use it directly with a key difference.

the `Cookie` expects a `value` field whereas the `Param` expects a `cookie` value.

If a cookie is defined and not sent properly when the call is made it will raise a `400` `BadRequest`.

## Response cookies

This is something else entirely and it is used when you want to send a cookie with the response. Very easy to use
as well.

The `response_headers` is a simple python list.

```python hl_lines="13-20"
{!> ../../../docs_src/extras/cookies/example3.py !}
```

When you check the response from the api call, you should now also have a `csrf` cookie being sent as well with the
value `CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz`.

This is how simple and effective you can manage response cookies.

## Caution

Although `Cookie` from response cookies looks very similar to `Cookie` from the `params`
**they are in fact very different.**

### Cookie from response cookies

This cookie is a datastructure that contains unique fields to create a `cookie` to be sent back in the response.

To import it:

```python
from esmerald.core.datastructures import Cookie

# or

from esmerald.core.datastructures import Cookie as ResponseCookie
```

### Cookie from params

The cookie used with the [example](#cookie-as-a-param) as param is not a datastructure but a `FieldInfo` so it cannot
be used to set and create a new `cookie` like the one from [response cookies](#response-cookies).

To import it:

```python
from esmerald import Cookie

# or

from esmerald.params import Cookie
```
