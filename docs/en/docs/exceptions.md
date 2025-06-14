# Exceptions

Esmerald comes with some built-in exceptions but also allows you to install
[custom exception handlers](./exception-handlers.md) to deal with how you return responses when exceptions happen.

## HTTPException

The `HTTPException` object serves as base that can be used for any handled exception from Esmerald.

```python
from esmerald.exceptions import HTTPException
```

### ImproperlyConfigured

The name might be familiar for some of the developers out there and it is intentional as it is also self explanatory.
Inherits from the base [HTTPException](#httpexception) and it is raised when a misconfiguration occurs.

```python
from esmerald.exceptions import ImproperlyConfigured
```

Status code: 500

### NotAuthenticated

Exception raised when an a resources that depends of an authenticated user does not exist.

```python
from esmerald.exceptions import NotAuthenticated
```

Status code: 401

### PermissionDenied

Exception raised when a [permission](./permissions/index.md) fails. It can be used in any context also outside of the
permissions context and it should be raised any time the access to a resource should be blocked.

```python
from esmerald.exceptions import PermissionDenied
```

Status code: 403

### ValidationErrorException

`ValidationErrorException` is part of the Esmerald default `exception_handlers` by design and it is part of its core when
a validation, for example, from pydantic models, occurs.

```python
from esmerald.exceptions import ValidationErrorException
```

Status code: 400

### NotAuthorized

Exception raised when an authentication fails. It is very useful for any authentication middleware process and it is
encouraged to be applied in any custom middleware handling with similar processes.

```python
from esmerald.exceptions import NotAuthorized
```

Status code: 401

### NotFound

Classic and self explanatory exception. Useful when a resource is not found or a simple 404 needs to be raised.

```python
from esmerald.exceptions import NotFound
```

Status code: 404

### MethodNotAllowed

Very useful exception to be used, as already is, to raise exceptions when an HTTP method is not allows on a given
Gateway.

```python
from esmerald.exceptions import MethodNotAllowed
```

Status code: 405

### InternalServerError

Used internally for internal server error and it raises a descriptive message in the browser if `debug=True`.

```python
from esmerald.exceptions import InternalServerError
```

Status code: 500

### ServiceUnavailable

It should be used to be raised when a resource is not available.

```python
from esmerald.exceptions import ServiceUnavailable
```

Status code: 503


### ValidatorError

This is a special exception that can be applied to anything in Esmerald. This allows to not only throw a normal
exception but filter it out the "noise" that can be caused by using an external library and provide a simple response.

```python
from esmerald.exceptions import ValidationError
```

Status code: 400

#### Example

Imagine you are using a library such as Pydantic (to simplify the example) and you want to throw a simple exception
that does not rely on a `ValueError` but you also want to provide some details.

```python
from esmerald import Esmerald, post
from esmerald.exceptions import ValidationError

from pydantic import BaseModel, model_validator


class PasswordIn(BaseModel):
    password: str
    retype_password: str

    @model_validator(mode="after")
    def validate_value(self):
        if self.password != self.retype_password
            raise ValidationError({'password': "Passwords do not match"})
        return self


@post('/password')
async def check(data: PasswordIn) -> None:
    ...
```

When a response fails, it should throw an error similar to this:

```json
{"detail": {"password": "Passwords do not match"}}
```

This can be particularly useful mostly if you want to create custom error messages and to be easy to parse a response
back to a client.

You can use the `ValidationError` in different way. As a `list`, `tuple`, `str` and `dict` and you can also override the
default `status_code`.

```python
from esmerald.exceptions import ValidationError

ValidationError("An error") # as string
ValidationError({"field": "an error" }) # as dict
ValidationError(["An error", "another error"]) # as list
ValidationError(("An error", "another error")) # as tuple
ValidationError("Not Authorized", status_code=401) # override the status_code
```

## Custom exceptions

Every application has different needs, errors, operations and everything else. Although the default Esmerald exceptions
work for generic and internal processing you might face an issue when it comes to handle some specifc, more narrow and
unique to your application type of exception. This is very simple and also very possible.

```python
{!> ../../../docs_src/exceptions/custom_exception.py !}
```

The example above of course is forced to be like that for illustration purposes to raise the custom exception as the
default if no `Optional` fields were declared would be handled by Esmerald `ValidationErrorException` exception
handler but this serves as an example how to do your own.

## Overriding the current Esmerald exception handlers

Currently by default, every Esmerald application starts with `ImproperlyConfigured` and `ValidationErrorException`
to make sure everything is covered accordingly but this does not necessarily mean that this can't be changed.

```python hl_lines="18 42 61-62"
{!> ../../../docs_src/exceptions/overriding.py !}
```

This will make sure that the application defaults will have a your exception_handler instead of the main application.

## API Reference

Check out the [API Reference for HTTPException](./references/exceptions.md) for more details.
