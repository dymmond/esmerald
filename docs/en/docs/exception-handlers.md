# Exception Handlers

This section is a complement to [exceptions](./exceptions.md) and more focused on the exception handler themselves.

Exception handlers are, as the name suggests, the handlers in case an exception of type X occurs in any
[level of an Esmerald application](./application/levels.md).

## Exception handlers and the application levels

In every level the `exception_handler` parameter (among others) are available to be used and handle specific exeptions
raised on each level.

The exception handlers are read from top-down in a python dictionary format, which means if you have the same exception
being raised on different levels but **different exception handlers** handling them,
**the last one takes the priority**.

```python hl_lines="15 31 59-61 66-68"
{!> ../../../docs_src/exception_handlers/precedent.py !}
```

### What is happening

The application level contains an exception handler `validation_error_exception_handler` and that means that for
every `ValidationErrorException` being raised in the application it will be handled by that function **except** the
`Gateway` that has its own handler `validation_error_gateway`.

The Gateway having its own exception handler to manage the `ValidationErrorException` takes precedent when the
endpoint is called and the exception is raised.

{! ../../../docs_src/_shared/exceptions.md !}

The same is applied also to [dependencies](./dependencies.md).


### Custom exception handlers

We all know that Esmerald handles really well the exceptions by design but sometimes we might also
want to throw an error while doing some code logic that is not directly related with a `data` of
an handler.

For example.

```python
{!> ../../../docs_src/exception_handlers/example.py !}
```

This example is a not usual at all but it serves to show where an exception is raised.

Esmerald offers **one** out of the box **custom exception handlers**:

* **value_error_handler** - When you want the `ValueError` exception to be automatically parsed
into a JSON.

```python
from esmerald.exception_handlers import value_error_handler
```

How it would look like the previous example using this custom exception handler?

```python hl_lines="21-23"
{!> ../../../docs_src/exception_handlers/example_use.py !}
```

Or if you prefer to place it on a Gateway level.

```python hl_lines="22-25"
{!> ../../../docs_src/exception_handlers/example_use_gateway.py !}
```

Or even specific only to the handler itself.

```python hl_lines="14-16"
{!> ../../../docs_src/exception_handlers/example_use_handler.py !}
```

As you can see, you can use this exception handler directly or as usual, you can create one of
your own and apply on every [application level](./application/levels.md).
