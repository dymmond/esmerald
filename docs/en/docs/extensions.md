# Extensions

What are extensions in an Ravyn context? A separate and individual piece of software that
can be hooked into **any** Ravyn application and perform specific actions individually without
breaking the ecosystem.

A feature that got a lof of inspirations from the great frameworks out there but simplified for
the Ravyn ecosystem.

Take Django as example. There are hundreds, if not thousands, of plugins for Django and usually,
not always, the way of using them is by adding that same pluggin into the `INSTALLED_APPS` and
go from there.

Flask on the other hand has a pattern of having those plugin objects with an `init_app` function.

Well, what if we could have the best of both? [Ravyn](./application/applications.md) as you
are aware is extremely flexible and dynamic in design and therefore having an `INSTALLED_APPS`
wouldn't make too much sense right?

Also, how could we create this pattern, like Flask, to have an `init_app` and allow the application
to do the rest for you? Well, Ravyn now does that via its internal protocols and interfaces.

!!! Note
    Extensions only exist on an [application level](./application/levels.md#application-levels).

## Pluggable

This object is one of a kind and does **a lot of magic** for you when creating an extension for
your application or even for distribution.

A **Pluggable** is an object that receives an [Extension](#extension) class with parameters
and hooks them into your Ravyn application and executes the [extend](#extend) method when
starting the system.

```python hl_lines="27 29"
{!> ../../../docs_src/pluggables/pluggable.py !}
```

It is this simple but is it the only way to add a pluggable into the system? **Short answser is no**.

More details about this in [hooking a pluggable into the application](#hooking-pluggables-and-extensions).

## Extension

This is the main class that should be extended when creating a pluggable for Ravyn.

This object internally uses the protocols to make sure you follow the patterns needed to hook
a pluggable via `pluggables` parameter when instantiating an ravyn application.

When subclassing this object **you must implement** the [extend](#extend) function. This function is what
Ravyn looks for when looking up for pluggables for your application and executes the logic.

Think of the `extend` as the `init_app` of Flask but enforced as a pattern for Ravyn.

```python hl_lines="7 13"
{!> ../../../docs_src/pluggables/extension.py !}
```

### extend()

The **mandatory** function that **must be implemented** when creating an extension to be plugged
via [Pluggable](#pluggable) into Ravyn.

It is the entry-point for your extension.

The extend by default expects `kwargs` to be provided but you can pass your own default parameters
as well as there are many ways of creating and [hooking a pluggable]

## Hooking pluggables and extensions

As mentioned before, there are different ways of hooking a pluggable into your Ravyn application.

### The automated and default way

When using the default and automated way, Ravyn expects the pluggable to be passed into a dict
`extensions` upon instantiation of an Ravyn application with `key-pair` value entries and where
the `key` is the name for your pluggable and the `value` is an instance [Pluggable](#pluggable)
holding your [Extension](#extension) object.

When added in this way, Ravyn internally **hooks** your pluggable into the application and
starts it by calling the [extend](#extend) with the provided parameters, automatically.

The `app` parameter is automatically injected by Ravyn and does not need to be passed as
parameter if needed

```python hl_lines="27 29"
{!> ../../../docs_src/pluggables/pluggable.py !}
```

You can access all the extensions of your application via `app.extensions` at any given time.

#### Reordering

Sometimes there are dependencies between extensions. One requires another.
You can reorder the extending order by using the method `ensure_extension(name)` of `app.extensions`.
It will fail if the extension doesn't exist, so only call it in extend.

{!> ../../../docs_src/pluggables/reorder.py !}

### The manual and independent way

Sometimes you simply don't want to start the pluggable inside an Ravyn instance automatically
and you simply want to start by yourself and on your own, very much in the way Flask does with
the `init_app`.

This way you don't need to use the [Pluggable](#pluggable) object in any way and instead you can
simply just use the [Extension](#extension) class or even your own since you **are in control**
of the extension.

There are two variants how to do it:

```python title="With extension class or Pluggable"
{!> ../../../docs_src/pluggables/manual.py !}
```

```python hl_lines="25 42-43" title="Self registering"
{!> ../../../docs_src/pluggables/manual_self_registering.py !}
```

You can use for the late registration the methods `add_extension`.
It will automatically initialize and call extend for you when passing a class or **Pluggable**,
**but not when passing an instance**.

### Standalone object

But, what if I don't want to use the [Extension](#extension) object for my pluggable? Is this
possible?
´
Yes, it must only implement the ExtensionProtocol.

```python hl_lines="9 25"
{!> ../../../docs_src/pluggables/standalone.py !}
```

## Important notes

As you can see, **extensions** in Ravyn can be a powerful tool that isolates common
functionality from the main Ravyn application and can be used to leverage the creation of plugins
to be used across your applications and/or to create opensource packages for any need.

## ChildRavyn and pluggables

An [Extension](#extension) **is not the same** as a [ChildRavyn](./routing/router.md#child-ravyn-application).

These are two completely independent pieces of functionality with completely different purposes, be
careful when considering one and the other.

Can a [ChildRavyn](./routing/router.md#child-ravyn-application) be added as a pluggable?
Of course.

You can do whatever you want with a pluggable, that is the beauty of this system.

Let us see how it would look like if you had a pluggable where the goal was to add a **ChildRavyn**
into the current applications being plugged.

```python hl_lines="33"
{!> ../../../docs_src/pluggables/child_ravyn.py !}
```

Crazy dynamic, isn't it? So clean and so simple that you can do whatever you desire with Ravyn.

## Pluggables and the application settings

Like almost everything in Ravyn, you can also add the [Pluggables](#pluggable) via
[settings](./application/settings.md) instead of adding when you instantiate the application.

```python hl_lines="29-31"
{!> ../../../docs_src/pluggables/settings.py !}
```

And simply start the application.

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=AppSettings uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="AppSettings"; uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

If you prefer, you can also use the [settings_module](./application/settings.md#the-settings_module).

```python hl_lines="34"
{!> ../../../docs_src/pluggables/settings_module.py !}
```
