# Exception Handlers

This section is a complement to [exceptions](./exceptions.md) and more focused on the exception handler themselves.

Exception handlers are, as the name suggests, the handlers in case an exception of type X occurs in any
[level of an Esmerald application](./application/levels.md).

## Exception handlers and the application levels

In every level the `exception_handler` parameter (among others) are available to be used and handle specific exeptions
raised on each level.

The exception handlers are read from top-down in a python dictionary format, which means if you have the same exception
being raised on different levels but **different exception handlers** handling them, **the last one takes precedent**. 

```python hl_lines="15 31 59-61 66-68"
{!> ../docs_src/exception_handlers/precedent.py !}
```

### What is happening

The application level contains an exception handler `validation_error_exception_handler` and that means that for
every `ValidationErrorException` being raised in the application it will be handled by that function **except** the
`Gateway` that has its own handler `validation_error_gateway`.

The Gateway having it's own exception handler to manage the `ValidationErrorException` takes precedent when the
endpoint is called and the exception is raised.

{! ../docs_src/_shared/exceptions.md !}

The same is applied also to [dependencies](./dependencies.md).
