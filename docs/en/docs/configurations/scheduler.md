# SchedulerConfig

What does this even mean?

Well, this means that if you don't want to use [Asyncz][asyncz] for your own personal or applicational reasons, then
you can simply build your own configuration and plug the scheduler into Ravyn.

This is now possible due to the fact that Ravyn now implements the **SchedulerConfig**.

## How to import it

You can import the configuration from the following:

```python
from ravyn.contrib.schedulers import SchedulerConfig
```

## The SchedulerConfig class

When implementing a scheduler configurations **you must implement** two functions.

1. [async def start()](#the-start-function)
2. [async def shutdown()](#the-shutdown-function)

This is what makes the SchedulerConfig modular because there are plenty of schedulers out there and each one of them
with a lot of different options and configurations but the one thing they all have in common is the fact that all
of them must start and shutdown at some point. The only thing Ravyn "cares" is that by encapsulating that functionality
into two simple functions.

### The start function

The start function, as the name suggests, its the function that Ravyn calls internally to start the scheduler for you.
This is important because when the `enable_scheduler` flag is set, it will look for the scheduler config and call the
`start` on startup.

### The shutdown function

The shutdown function, as the name suggests, its the function that Ravyn calls internally to shutdown the scheduler for you.
This is important because when the `enable_scheduler` flag is set, it will look for the scheduler config and call the
`shutdown` on shutdown (usually when the application stops).

### How to use it

Ravyn already implements this interface with the custom `AsynczConfig`. This functionality is very handy since Asyncz
has a lot of configurations that can be passed and used within an Ravyn application.

Let us see how the implementation looks like.

```python
{!> ../../../docs_src/scheduler/asyncz.py !}
```

We won't be dueling on the technicalities of this configuration because its unique to Asyncz provided by Ravyn but
**it is not mandatory to use it as you can build your own** and pass it to Ravyn `scheduler_config` parameter.

### SchedulerConfig and application

To use the `SchedulerConfig` in an application, like the one [shown above with asyncz](#how-to-use-it), you can simply do this:

!!! Note
    We use the existing AsynczConfig as example but feel free to use your own if you require something else.

```python
{!> ../../../docs_src/scheduler/example.py !}
```

If you want to know [more about how to use the AsynczConfig](../scheduler/index.md), check out the section.

### Application lifecycle

Ravyn scheduler is tight to the application lifecycle and that means the `on_startup/on_shutdown` and `lifespan`.
You can [read more about this](../lifespan-events.md) in the appropriate section of the documentation.

By default, the scheduler is linked to `on_startup/on_shutdown` events and those are automatically managed for you
**but if you require the lifespan** instead, then you must do the appropriate adjustments.

The following example serves as a suggestion but feel free to use your own design. Let us check how we could manage
this using the `lifespan` instead.

```python
{!> ../../../docs_src/scheduler/example2.py !}
```

Pretty easy, right? Ravyn then understands what needs to be done as normal.

### The SchedulerConfig and the settings

Like everything in Ravyn, the SchedulerConfig can be also made available via settings.

```python
{!> ../../../docs_src/scheduler/via_settings.py !}
```

## Important Notes

- You can create your own [custom scheduler config](#how-to-use-it).
- You **must implement** the `start/shutdown` functions in any scheduler configuration.
- You can use or `on_startup/shutdown` or `lifespan` events. The first is automatically managed for you.

[asyncz]: https://asyncz.dymmond.com
