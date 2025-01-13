# Dependencies

Dependencies are a piece of great functionality now common in a lot of the frameworks out there and allows the concept
of dependency injection to take place.

Esmerald uses the `Inject` object to manage those dependencies in every
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

## More real world examples

Now let us imagine that we have a web application with one of the views. Something like this:

```python hl_lines="17"
{!> ../../../docs_src/dependencies/controllers.py !}
```

As you can notice, the `user_dao`` is injected automatically using the appropriate level of dependency injection.

Let us see the `urls.py` and understand from where we got the `user_dao`:

```python hl_lines="14-16 32-34"
{!> ../../../docs_src/dependencies/urls.py !}
```

In the previous example we use lambdas to create a callable from DAO instances and we refactor it
to use the `Factory` object instead. It is cleaner and more pleasant to work with.

The cleaner version of lambdas using Esmerald it is called `Factory`.

!!! Note
    You can see the Python lambdas as the equivalent of the anonymous functions in JavaScript.
    If you are still not sure, [see more details](https://www.w3schools.com/python/python_lambda.asp) about it.


!!! Tip
    Learn more about Esmerald [DAOs](./protocols.md) and how to take advantage of those.


The Factory is a clean wrapper around any callable (classes usually are callables as well, even without instantiating the object itself).

!!! Tip
    No need to explicitly instantiate the class, just pass the class definition to the `Factory`
    and Esmerald takes care of the rest for you.

### Importing using strings

Like everything is Esmerald, there are different ways of achieving the same results and the `Factory`
is no exception.

In the previous examples we were passing the `UserDAO`, `ArticleDAO` and `PostDAO` classes directly
into the `Factory` object and that also means that **you will need to import the objects to then be passed**.

What can happen with this process? Majority of the times nothing **but** you can also have the classic
`partially imported ...` annoying error, right?

Well, the good news is that Esmerald got you covered, as usual.

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
    Both cases work well within Esmerald, this is simply an alternative in case the complexity of
    the codebase increases and you would like to tidy it up a bit more.

In conclusion, if your views/routes expect dependencies, you can define them in the upper level as described
and Esmerald will make sure that they will be automatically injected.

## `Requires` and `Security`

From the version 3.6.3+, Esmerald allows also to use what we call a "simpler" dependency injection. This dependency
injection system does not aim replace the current sytem but aims to provide another way of using some dependencies
in a simpler fashion.

The `Security` object is used, as the name suggests, to implement the out of the box [security provided by Esmerald](./security/index.md)
and in that section, that is explained how to apply whereas te `Requires` implements a more high level dependency system.

You can import directly from `esmerald`:

**Requires**

```python
from esmerald import Requires
```

**Security**

```python
from esmerald import Requires
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

Now this is where things start to get interesting. Esmerald operates in layers and **almost** everything works like that.

What if you want to use the requires to operate on a layer level? Can you do it? **Yes**.

It works as we normally declare dependencies, for example, a [Factory](#more-real-world-examples) object.

```python
{!> ../../../docs_src/dependencies/requires/layer.py !}
```

### Security within the Requires

You can mix `Security()` and `Requires()` without any issues as both subclass the same base but there are nuances compared to
the direct application of the `Security` without using the `Requires` object.

For more details how to directly use the Security without using the Requires, please check the [security provided by Esmerald](./security/index.md)
section where it goes in into detail how to use it.

```python
from lilya.middleware.request_context import RequestContextMiddleware
from lilya.middleware import DefineMiddleware


app = Esmerald(
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

The `Security()` object is used **only** when you want to apply the niceties of [Esmerald security](./security/index.md)
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

There many ways of implementing the dependency injection in Esmerald:

* Using the layers with `Inject` and `Injects()` respectively.
* Using the `Factory()` within and `Inject()` and `Injects()`.
* Using `Requires()` within an `Inject()` and `Injects()`.
* Using `Security()` within an `Inject()` and `Injects()` or within a `Requires()`.
* Using `Requires()` without using an `Inject()` and `Injects()` limiting it to the handler and **not application layer dependency**.
*
