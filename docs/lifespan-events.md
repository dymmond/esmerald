# Lifespan Events

These are extremely common for the cases where you need to define logic that should be execute
before the application starts and shuts down.

Before starting means the code (logic) will be executed **once** before starting receiving requests
and the same is for the shutting down where the logic is also executed **once** after having managed,
quite possibly, many requests.

This can be particularly useful for setting up your application resources and cleaning them up.
These cycles cover the **whole** application.

## Types of events

Currently Esmerald supports **on_startup**, **on_shutdown** and **lifespan**.

Esmerald being built on the top of Lilya, it inherited those behaviours, which means, it can be
easily assembled to work directly with these events 🤖.

### Esmerald on_startup and on_shutdown

If you pass an `on_startup` and an `on_shutdown` parameters intead of the `lifespan`, Esmerald
will **automatically generate the async context manager** for you and pass it to the `lifespan`
internally for you.

This way Esmerald assures 100% compatibility with Lilya and still maintains the same
"look and feel" as before.

**You can use on_startup/on_shutdown and lifespan but not both at the same time**.

!!! Tip
    The `shutdown` usually happens when you stop the application.

### Functions

To define the functions to be used within the events, you can define a `def` or `async def`
function. Esmerald will know what to do with those and handle them for you.

## How to use

Using these events is actually pretty much clear and simply. As mentioned before, there are two ways:

1. Via [on_startup and on-shutdown](#on_startup-and-on_shutdown)
2. Via [lifespan](#lifespan)

Nothing like a use case to understand this better.

Let us assume you want to add a database into your application and because this can be costly, you
also do not want to do it for every request, you then want this on an application level to be done
**on starting up** and close **on shutting down**.

Let us then see how that it would look like using the current available events.

We will be using [Saffier](https://saffier.tarsild.io) as example as it is also supoprted by
Esmerald.

### on_startup and on_shutdown

This is the classic approach and widely used until the new [lifespan](#lifespan) came out as a new
standard.

This type of approach is still being implemented in a lot of the pluggins used out there.

Using the database use case defined above:

```python hl_lines="25-26"
{!> ../docs_src/events/start_shutdown.py !}
```

As you can see, when the application is starting up, we declared the `database.connect()` to happen
as well as the `database.disconnect()` on shutting down.

### Lifespan

What happens if we use the [example above](#on_startup-and-on_shutdown) and convert it to a
lifespan event?

Well, this one although is also very simple, the way is assembled is slighly different.

To define the *startup* and *shutown* events, you will need a *context manager* to make it happen.

Let us see what does it mean in practical examples by changing the previous one to a `lifespan`.

```python hl_lines="25-26 36"
{!> ../docs_src/events/lifespan.py !}
```

This is quite something to unwrap here. What is actually happening?

So, before you need to explicitly declare the `on_startup` and `on_shutdown` events in the
corresponding parameters in the Esmerald application but with the `lifespan` you do that in
**one place only**.

The first part before the `yield` will be executed **before the application starts** and
the second part after the `yield` will be executed **after the application is finished**.

The `lifespan` function takes an `app: Esmerald` as a parameter because is then injected into
the application and the framework will know what to do with it.

### Async context manager

As you can check, the [lifespan](#lifespan) functiom is decorated with an `@asynccontextmanager`.

This is standard python for using a `decorator` and this one in particular converts the `lifespan`
function into something called **async context manager**.

```python hl_lines="1 25"
{!> ../docs_src/events/lifespan.py !}
```

In Python, a **context manager** is something that you can use with the `with` keyword. One widely
used, for example, is with the `open()`.

```python
with open("file.txt", 'rb') file:
    file.read()
```

When a context manager or async context manager is created like the example above, what it does it
that before entering the `with` it will execute the code **before** the `yield` and when exiting
the code block, it wille excute the code **after** the `yield`.

The lifespan parameter of Esmerald takes an **async context manager** which means we can ass our
new `lifespan` async context manager directly to it.

## Curiosity about async context managers

This section is out of the scope of the lifespan and events of Esmerald and it is
**for curiosity only**. Please see the [lifespan](#lifespan) section as in the case of Esmerald,
the way of **declaring is different** and an `app: Esmerald` parameter is **always required**.

### General approach to async context managers

In general when using an async context the principle is the same as a normal context manager with
the key difference that we use `async` before the `with`.

Let use see an example still using the [Saffier](https://saffier.tarsild.io) ORM.

!!! Warning
    Again, this is for general purposes, not for the use of the Esmerald lifespan. That example
    how to use it is described in the [lifespan](#lifespan) section.

#### Using functions

```python hl_lines="1 9-10 16"
{!> ../docs_src/events/curiosities/example.py !}
```

As you can see, we used the `@asynccontextmanager` to transform our function into an `async`
context manager and the `yield` is what manages the `enter` and `exit` behaviour.

#### Using Python classes

What if we were to build one async context manager with Python classes? Well this is actually
even better as you can "visually" see and understand the behaviour.

Let us get back to the same example with [Saffier](https://saffier.tarsild.io) ORM.

```python hl_lines="9-10 13-14 17"
{!> ../docs_src/events/curiosities/classes.py !}
```

This example is actually very clear. The `aenter` is the equivalent to what happens before the
`yield` in our previous example and the `aexit` is what happens after the `yield`.

This time the `@asynccontextmanager` wasn't necessary to decorate the class. The behaviour
implemented by that is done via `aenter` and `aexit`.

Async context managers can be a powerful tool in your application.
