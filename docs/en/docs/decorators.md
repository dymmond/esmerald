# Decorators

## What are Decorators?

Decorators in Python are a powerful feature that allows you to modify the behavior of functions or classes.
They are commonly used to extend functionality without modifying the actual implementation.

In Ravyn, decorators play a crucial role in defining various aspects of an application, such as security,
caching, and request handling.

## Benefits of Using Decorators

- **Code Reusability**: Allows adding functionality across multiple classes or functions without repetition.
- **Separation of Concerns**: Keeps logic modular and clean by applying behaviors externally.
- **Enhanced Readability**: Clearly defines additional behavior without cluttering function or class definitions.
- **Maintainability**: Reduces code duplication and enhances scalability.

## The `@controller` Decorator

The `@controller` decorator in Ravyn transforms a class into a Controller, allowing it to manage and structure
routes efficiently.

This decorator enhances class-based views and provides a clean, structured way to define routes in Ravyn applications.

This also provides an alternative to subclassing the [Controller](./routing/apiview.md#apiview) class directly.

### Benefits of `@controller`

- **Organizes Routes**: Allows grouping related route handlers inside a class.
- **Inherits Controller Behavior**: Automatically extends Ravyn’s `Controller` class.
- **Encapsulation**: Keeps route-related logic within a single class.
- **Enhances Maintainability**: Improves the readability and scalability of route management.

## How to Use `@controller`

The `@controller` decorator takes optional keyword arguments to configure the controller’s behavior. These include:

- `path`: Defines the base path for all routes within the controller.
- `dependencies`: Injects dependencies into the controller.
- `exception_handlers`: Defines custom exception handlers.
- `permissions`: Adds security permissions.
- `interceptors`: Allows request/response interception.
- `middleware`: Applies middleware at the controller level.
- `response_class`, `response_cookies`, `response_headers`: Controls responses.
- `before_request`, `after_request`: Defines lifecycle hooks.
- `tags`: Adds OpenAPI documentation tags.
- `include_in_schema`: Includes/excludes from API documentation.
- `security`: Configures security schemes.
- `deprecated`: Marks the controller as deprecated in the documentation.

## Example Usage

### Defining a Basic Controller

```python
{!> ../../../docs_src/utils/controller.py !}
```

### Explanation

1. `@controller(path="/users")`: Registers the `UserController` with a base path `/users`.
2. `@get(path="/")`: Defines a `GET` endpoint at `/users/`.
3. `@post(path="/create")`: Defines a `POST` endpoint at `/users/create`.
4. `response_headers`: Adds custom response headers to the API response.
5. The controller encapsulates all user-related logic, keeping the structure organized.

By using the `@controller` decorator, Ravyn applications become more modular, maintainable, and scalable.

The decorator streamlines route definitions while leveraging built-in Ravyn capabilities.
