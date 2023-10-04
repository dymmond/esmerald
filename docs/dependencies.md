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

#### What is happening

The `number` is obtained from the `first_dependency` and passed to the `second_dependency` as a result and validates
and checks if the value is bigger or equal than 5 and that result `is_valid` is than passed to the main handler
`/validate` returning a bool.

{! ../docs_src/_shared/exceptions.md !}

The same is applied also to [exception handlers](./exception-handlers.md).

## More real world examples

Now let us imagine that we have a web application with one of the views. Something like this:

```python hl_lines="17"
{!> ../docs_src/dependencies/views.py !}
```

As you can notice, the `user_dao`` is injected automatically using the appropriate level of dependency injection.

Let us see the `urls.py` and understand from where we got the `user_dao`:

```python hl_lines="14-16 32-34"
{!> ../docs_src/dependencies/urls.py !}
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
{!> ../docs_src/dependencies/urls_factory_import.py !}
```

Now, this is a beauty is it not? This way, the codebase is cleaner and without all of those imported
objects from the top.

!!! Tip
    Both cases work well within Esmerald, this is simply an alternative in case the complexity of
    the codebase increases and you would like to tidy it up a bit more.

In conclusion, if your views/routes expect dependencies, you can define them in the upper level as described
and Esmerald will make sure that they will be automatically injected.
