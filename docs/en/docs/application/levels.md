# Application levels

An Ravyn application is composed by levels and those levels can be [Gateway](../routing/routes.md#gateway),
[WebSocketGateway](../routing/routes.md#websocketgateway), [Include](../routing/routes.md#include),
[handlers](../routing/handlers.md) or even **another Ravyn** or
[ChildRavyn](../routing/router.md#child-ravyn-application).

There are some levels in the application, let's use an example.

```python
{!> ../../../docs_src/application/app/levels.py !}
```

**Levels**:

1. [Ravyn](./applications.md) - The application instance.
2. [Include](../routing/routes.md#include) - The second level.
3. [Gateway](../routing/routes.md#gateway) - The third level, inside an include.
4. [Handler](../routing/handlers.md) - The forth level, the Gateway handler.

You can create as many levels as you desire. From nested includes to
[ChildRavyn](../routing/router.md#child-ravyn-application) and create your own design.

## With a ChildRavyn

```python hl_lines="49 58"
{!> ../../../docs_src/application/app/child_esmerald_level.py !}
```

**Levels**:

1. [Ravyn](./applications.md) - The application instance. **First Level**.
2. [Gateway](../routing/routes.md#gateway) - The **second level**, inside the app routes.
    1. [Handler](../routing/handlers.md) - The **third level**, inside the Gateway.
3. [WebSocketGateway](../routing/routes.md#websocketgateway) - The **second level**, inside the app routes.
    1. [Handler](../routing/handlers.md) - The **third level**, inside the WebSocketGateway.
4. [Include](../routing/routes.md#include) - The **second leve**l. Inside the app routes.
    1. [ChildRavyn](../routing/router.md#child-ravyn-application) - The **third level** inside the include and
also **first level** as independent instance.
        1. [Gateway](../routing/routes.md#gateway) - The **second level**, inside the `ChildRavyn`.
            1. [Handler](../routing/handlers.md) - The **second level**, inside the Gateway.

!!! Warning
    A `ChildRavyn` is an independent instance that is plugged into a main `Ravyn` application, but since
    it is like another `Ravyn` object, that also means the `ChildRavyn` does not take precedence over the top-level
    application, instead, treats its own [Gateway](../routing/routes.md#gateway),
    [WebSocketGateway](../routing/routes.md#websocketgateway), [Include](../routing/routes.md#include),
    [handlers](../routing/handlers.md) or even another `Ravyn` or
    [ChildRavyn](../routing/router.md#child-ravyn-application) and parameters in **isolation**.

## Exceptions

`ChildRavyn`, as per **warning** above, has its own rules, but there are always exceptions to any almost every rule.
Although it is an independent instance with its own rules, this is not applied to **every** parameter.

[Middlewares](../middleware/middleware.md) and [Permissions](../permissions/index.md) are actually global and the rules of
precedence can be applied between an `Ravyn` instance and the corresponding `ChildRavyn` apps.

In other words, you **don't need** to create/repeat the same permissions and middlewares (common to both) across
every instance. They can be applied **globally** from the top main `Ravyn` object.

```python hl_lines="97-99 108 115 117-118"
{!> ../../../docs_src/application/app/permissions_and_middlewares.py !}
```

### Notes

The example given is intentionally big and "complex" simply to show that even with that complexity in place,
the `middleware` and `permissions` remained global to the whole application without the need to implement
on both `Ravyn` and `ChildRavyn`.
