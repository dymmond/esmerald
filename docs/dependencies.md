# Dependencies

Dependencies are a piece of great functionality now common in a lot of the frameworks out there and allows the concept
of dependency injection to take place.

Esmerald uses the `Inject` object to manage those dependencies in every
[application level](./exception-handlers.md)

## Dependencies and the application levels

In every level the `dependencies` parameter (among others) are available to be used and handle specific dependencies
raised on each level.

The dependencies are read from top-down in a python dictionary format, which means
**the last one takes the priority**.

## How to use

Assuming we have a `User` model using [Saffier](./databases/saffier/models.md).

```python hl_lines="14-15 19"
{!> ../docs_src/dependencies/precedent.py !}
```

The example above is very simple and of course a user can be obtained in a slighly and safer way but for it serves only
for example purposes.

Using dependencies is quite simple, it needs:

1. Uses `Inject` object.
2. Uses the `Injects` object to, well, inject the dependency into the handler.

### Some complexity

Dependencies can be injected in many levels as previously referred and that also means, you can implement the levels of
complexity you desire.

```python hl_lines="4 8 21-23 26"
{!> ../docs_src/dependencies/more_complex.py !}
```

#### What is happenening

The `number` is obtained from the `first_dependency` and passed to the `second_dependency` as a result and validates
and checks if the value is bigger or equal than 5 and that result `is_valid` is than passed to the main handler
`/validate` returning a bool.

{! ../docs_src/_shared/exceptions.md !}

The same is applied also to [exception handlers](./exception-handlers.md).
