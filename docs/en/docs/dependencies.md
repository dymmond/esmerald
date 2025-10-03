# Dependencies

Dependencies are a piece of great functionality now common in a lot of the frameworks out there and allows the concept
of dependency injection to take place.

Ravyn uses the `Inject` object to manage those dependencies in every
[application level](./application/levels.md)

## Dependencies and the application levels

In every level the `dependencies` parameter (among others) are available to be used and handle specific dependencies
raised on each level.

The dependencies are read from top-down in a python dictionary format, which means
**the last one takes the priority**.

## How to use

Assuming we have a `User` model using [Edgy](./databases/edgy/models.md).

```python hl_lines="14-15 19"
{!> ../../../docs_src/dependencies/precedent.py !}
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
{!> ../../../docs_src/dependencies/more_complex.py !}
```

#### What is happening

The `number` is obtained from the `first_dependency` and passed to the `second_dependency` as a result and validates
and checks if the value is bigger or equal than 5 and that result `is_valid` is than passed to the main handler
`/validate` returning a bool.

{! ../../../docs_src/_shared/exceptions.md !}

The same is applied also to [exception handlers](./exception-handlers.md).

## Use without `Inject`

Ravyn allows you to use the callable directly without using the `Inject` object.

What does this mean? Well, internally Ravyn checks if its an Inject object and if not, it will automatically
create an `Inject` object for you. This means that you can use the callable directly without using the `Inject` object.

```python
{!> ../../../docs_src/dependencies/no_inject.py !}
```

This is a great way to use the dependencies without having to worry about the `Inject` object and just use the
callable directly.

This is also applied to the `Factory` (below) or to any callable that you want to use.

## The usage of the `Factory`

The `Factory` class serves as a **dependency provider** for Ravyn's dependency injection system.
It allows developers to register a class or function as a dependency that will be instantiated or invoked whenever needed.
Instead of manually creating instances across multiple parts of an application, `Factory` ensures a
**centralized and automated way** to manage dependencies.

This is particularly useful in frameworks like Ravyn, where dependency injection plays a key role in managing
resources, services, and business logic components efficiently.

One of the **primary benefits** of using `Factory` is that it supports **both direct callables and string-based imports**,
making it flexible for various use cases.

When a string is provided, the application dynamically loads the required module and resolves the attribute,
enabling a **decoupled structure** where dependencies do not need to be imported explicitly everywhere.

Additionally, the `Factory` allows to accept arguments (`args` and `kwargs`), which means dependencies can be
instantiated with **custom parameters** rather than relying solely on default constructors.

From a **performance and maintainability** perspective, `Factory` helps **reduce boilerplate code**,
ensures **lazy instantiation** of dependencies (only creating instances when required),
and **improves testability** by allowing easy substitution of dependencies during unit testing.

This approach **enhances modularity**, making it easier to swap out implementations or introduce mock objects when needed.

In a **scalable** application, having a well-structured dependency injection system powered by `Factory`
ensures that component interactions remain **clean, efficient, and adaptable** to future changes.

**Example**

```python hl_lines="17"
{!> ../../../docs_src/dependencies/controllers.py !}
```
As you can notice, the `user_dao` is injected automatically using the appropriate level of dependency injection.

Let us see the `urls.py` and understand from where we got the `user_dao`:

```python hl_lines="14-16 32-34"
{!> ../../../docs_src/dependencies/urls.py !}
```

In the previous example we use lambdas to create a callable from DAO instances and we refactor it
to use the `Factory` object instead. It is cleaner and more pleasant to work with.

The cleaner version of lambdas using Ravyn it is called `Factory`.

!!! Note
    You can see the Python lambdas as the equivalent of the anonymous functions in JavaScript.
    If you are still not sure, [see more details](https://www.w3schools.com/python/python_lambda.asp) about it.


!!! Tip
    Learn more about Ravyn [DAOs](./protocols.md) and how to take advantage of those.


The Factory is a clean wrapper around any callable (classes usually are callables as well, even without instantiating the object itself).

!!! Tip
    No need to explicitly instantiate the class, just pass the class definition to the `Factory`
    and Ravyn takes care of the rest for you.

### Factory using `args`

This represents the usage of the explicit `args` to pass.

```python
{!> ../../../docs_src/dependencies/factory_args.py !}
```

### Factory using `kwargs`

This represents the usage of the explicit `args` and `kwargs` to pass.

```python
{!> ../../../docs_src/dependencies/factory_kwargs.py !}
```

!!! Tip
    You can also [not use the Inject()](#use-without-inject) when passing a Factory in the same way as it was
    explained in the [Use without Inject](#use-without-inject) section.

### Importing using strings

Like everything is Ravyn, there are different ways of achieving the same results and the `Factory`
is no exception.

In the previous examples we were passing the `UserDAO`, `ArticleDAO` and `PostDAO` classes directly
into the `Factory` object and that also means that **you will need to import the objects to then be passed**.

What can happen with this process? Majority of the times nothing **but** you can also have the classic
`partially imported ...` annoying error, right?

Well, the good news is that Ravyn got you covered, as usual.

The `Factory` **also allows import via string** without the need of importing directly the object
to the place where it is needed.

Let us then see how it would look like and let us then assume:

1. The `UserDAO` is located somewhere in the codebase like `myapp.accounts.daos`.
2. The `ArticleDAO` is located somewhere in the codebase like `myapp.articles.daos`.
3. The `PostDAO` is located somewhere in the codebase like `myapp.posts.daos`.

Ok, now that we know this, let us see how it would look like in the codebase importing it inside the
`Factory`.

```python hl_lines="13-15"
{!> ../../../docs_src/dependencies/urls_factory_import.py !}
```

Now, this is a beauty is it not? This way, the codebase is cleaner and without all of those imported
objects from the top.

!!! Tip
    Both cases work well within Ravyn, this is simply an alternative in case the complexity of
    the codebase increases and you would like to tidy it up a bit more.

In conclusion, if your views/routes expect dependencies, you can define them in the upper level as described
and Ravyn will make sure that they will be automatically injected.

## `Requires` and `Security`

The `Security` object is used, as the name suggests, to implement the out of the box [security provided by Ravyn](./security/index.md)
and in that section, that is explained how to apply whereas te `Requires` implements a more high level dependency system.

You can import directly from `ravyn`:

**Requires**

```python
from ravyn import Requires
```

**Security**

```python
from ravyn import Security
```

!!! Warning
    Neither `Requires()` or `Security()` are designed to work on an [application level](#dependencies-and-the-application-levels)
    as is. For application layers and dependencies, you **must still use the normal dependency injection system to make it work**
    or use the [Requires within the application layers](#requires-within-the-application-layers).

### Requires

This is what we describe a simple dependency.


An example how to use `Requires` would be something like this:

```python
{!> ../../../docs_src/dependencies/requires/simple.py !}
```

This example is very simple but you can extend to whatever you want and need. The `Requires` is not a Pydantic model
but a pure Python class. You can apply to any other complex example and having a `Requires` inside more `Requires`.

```python
{!> ../../../docs_src/dependencies/requires/nested.py !}
```

### Requires within the application layers

Now this is where things start to get interesting. Ravyn operates in layers and **almost** everything works like that.

What if you want to use the requires to operate on a layer level? Can you do it? **Yes**.

It works as we normally declare dependencies, for example, a [Factory](#more-real-world-examples) object.

```python
{!> ../../../docs_src/dependencies/requires/layer.py !}
```

### Security within the Requires

You can mix `Security()` and `Requires()` without any issues as both subclass the same base but there are nuances compared to
the direct application of the `Security` without using the `Requires` object.

For more details how to directly use the Security without using the Requires, please check the [security provided by Ravyn](./security/index.md)
section where it goes in into detail how to use it.

```python
from lilya.middleware.request_context import RequestContextMiddleware
from lilya.middleware import DefineMiddleware


app = Ravyn(
    routes=[...],
    middleware=[
        middleware=[DefineMiddleware(RequestContextMiddleware)],
    ]
)
```

!!! Warning
    You can mix both `Requires()` and `Security()` (**Security inside Requires**) but for this to work properly, you will
    **need to add the `RequestContextMiddleware` from Lilya** or an exception will be raised.

Now, how can we make this simple example work? Like this:

```python
{!> ../../../docs_src/dependencies/requires/security.py !}
```

This example is an short adaptation of [security using jwt](./security/oauth-jwt.md) where we update the dependency
to add a `Requires` that also depends on a `Security`.

The `Security()` object is used **only** when you want to apply the niceties of [Ravyn security](./security/index.md)
in your application.

It is also a wrapper that does some magic for you by adding some extras automatically. The `Security` object expects you
to have an instance that implements an `async __call__(self, connection: Request) -> Any:` in order to operate.

Let us see a quick example:

```python
{!> ../../../docs_src/dependencies/requires/example.py !}
```

#### Application layer

But what about you using the application layer architecture? Is it possible? Also yes. Let us update the previous example
to make sure we reflect that.

```python
{!> ../../../docs_src/dependencies/requires/security_layer.py !}
```

## Recap

There many ways of implementing the dependency injection in Ravyn:

* Using the layers with `Inject` and `Injects()` respectively.
* Using the `Factory()` within and `Inject()` and `Injects()`.
* Using `Requires()` within an `Inject()` and `Injects()`.
* Using `Security()` within an `Inject()` and `Injects()` or within a `Requires()`.
* Using `Requires()` without using an `Inject()` and `Injects()` limiting it to the handler and **not application layer dependency**.
*
