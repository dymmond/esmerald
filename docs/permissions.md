# Permissions

Authentication and authorization are a must in every application. Managing those via dependencies is extremely possible
and also widely used but with **Esmerald** you have a clear separation of permissions although still allowing
[inject](./dependencies.md) to happen as well.

Inspired by the same author of Django Rest Framework, Esmerald permissions are as simple as you want them to be and as complex
as you design. For all tastes.

!!! Note
    This permission system is not the same as the [Lilya permission system](https://lilya.dev/permissions).

## BasePermission and custom permissions

If you are used to Django Rest Framework, the way **Esmerald** designed was very much within the same lines and with
all the huge community of developer in mind to make a transition almost immediate and simple as possible.

All the permission classes **must derive** from `BasePermission`.

The permissions **must** implement the `has_permission` and return `True` or `False`.

The permissions can also be `async` in case you need to run awaitables.

**An example of a permission for an user admin**.

```python
{!> ../docs_src/permissions/permissions.py !}
```

**An example of a permission for an user admin with async**.

```python hl_lines="25"
{!> ../docs_src/permissions/async/permissions.py !}
```

**An example of a permission for a project**

```python
{!> ../docs_src/permissions/simple_permissions.py !}
```

**An example of a permission for a project with async**

```python hl_lines="10"
{!> ../docs_src/permissions/async/simple_permissions.py !}
```

## Esmerald and permissions

Esmerald giving support to [Saffier ORM](./databases/saffier/motivation.md) and [Edgy](./databases/edgy/motivation.md) also provides some default permissions
that can be linked to the models also provided by **Esmerald**.

### IsAdminUser and example of provided permissions

This is a simple permission that extends the `BaseAbstractUserPermission` and checks if a user is authenticated or not.
The functionality of verifying if a user might be or not authenticated was separated from the
[Saffier](./databases/saffier/motivation.md) and instead you must implement the `is_user_authenticated()`
function when inheriting from `BaseAbstractUserPermission` or `IsAdminUser`.

## Esmerald and provided permissions

Esmerald provides some default permissions that can be used in your projects but not too many as every project has
special needs and rules.

* **DenyAll** - As the name suggests, blocks access to anyone. Can be useful if an API is under maintenance.
* **AllowAny** - The opposite of DenyAll. Allows access to everyone. Useful as permission for the top Esmerald
application.
* **IsAdminUser** - Checks if a user is admin or not by inheriting the object and implementing `is_user_staff` function.
* **IsAuthenticated** - Checks if a user is authenticated by inheriting from the object and implementing the logic
for `is_user_authenticated` function.
* **IsAuthenticatedOrReadOnly** - Checks if a user is authenticated or a read only request. For the autenticated
part the `is_user_authenticated` needs to be implemented.

### How to use

To use the `IsAdminUser`, `IsAuthenticated` and `IsAuthenticatedOrReadOnly` is as simple as the example below.

```python hl_lines="33 35 42"
{!> ../docs_src/permissions/admin.py !}
```

1. The main app `Esmerald` has an `AllowAny` permission for the top level
2. The `UserAPIView` object has a `IsUserAuthenticated` allowing only authenticated users to access any
of the endpoints under the class (endpoints under `/users`).
3. The `/users/admin` has a permission `IsAdmin` allowing only admin users to access the specific endpoint

### More on permissions

The permissions internally are checked from top down which means you can place permissios at any
given part of the [level](./application/levels.md) making it more dynamic and allowing to narrow
it down to a granular level that is managenable.

Internally, Esmerald runs all the validations and checks and on an application level, the only
thing you need to make sure is to **implement the `has_permission`** on any derived class of
[BasePermission](#basepermission-and-custom-permissions).

## Permissions summary

1. All permissions must inherit from `BasePermission`.
2. `BasePermission` has the `has_permission(request Request, apiview: "APIGateHandler") and it can
be `async` or not.
3. The [handlers](./routing/handlers.md), [Gateway](./routing/routes.md#gateway),
[WebSocketGateway](./routing/routes.md#websocketgateway), [Include](./routing/routes.md#include)
and [Esmerald](./application/applications.md) can have as many permissions as you want.

## API Reference

Check out the [API Reference for Permissions](./references/permissions.md) for more details.
