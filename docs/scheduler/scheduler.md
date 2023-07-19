# Motivation

Almost every application in one way or another needs some sort of automated scheduler to run automated tasks.
In that in mind and with the help of the great widely used
<a href='https://asyncz.tarsild.io' target='_blank'>Asyncz</a>, Esmerald comes with a built-in
scheduler, saving you tons of headaches and simplifying the process of creating them.

## Requirements

Esmerald uses `asyncz` for this integration. You can install by running:

```shell
$ pip install esmerald[schedulers]
```

## EsmeraldScheduler

The `EsmeraldScheduler` is the main object that manages the internal scheduler of `Esmerald` expecting:

* `app` - The Esmerald application. Automatically passed upon creating an Esmerald instance.
* `scheduler_class` - An instance of the `Asyncz` schedule type. Passed via `scheduler_class`.

    <sup>Default: `AsyncIOScheduler`</sup>

* `tasks` - A python dictionary of both key, value string mapping the tasks. Passed via
`scheduler_tasks`.

    <sup>Default: `{}`</sup>

* `timezone` - The `timezone` of the scheduler. Passed via `timezone`.

    <sup>Default: `UTC`</sup>

* `configurations` - A python dictionary containing some extra configurations for the scheduler.
Passed via `scheduler_configurations`.

Since `Esmerald` is an `ASGI` framework, it is already provided a default scheduler class that works alongside with
the application, the `AsyncIOScheduler`.

If a `scheduler_class` is not provided while the `enable_scheduler` is true, it will raise an error 500
[ImproperlyConfigured](../exceptions.md#improperlyconfigured).

!!! Note
    This is for representation and explanation purposes as the EsmeraldScheduler cannot be instantiated,
    instead, expects parameters being sent upon creating an Esmerald application.

```python hl_lines="4"
from esmerald import Esmerald
from asyncz.schedulers import AsyncIOScheduler

app = Esmerald(scheduler_class=AsyncIOScheduler)
```

You can have your own scheduler class as long as it is compatible with Esmerald, meaning, ASGI.

!!! warning
    Anything else that does not work with `AsyncIO` is very likely also not to work with Esmerald.

## EsmeraldScheduler and the application

The `EsmeraldScheduler` class is not accessible in any part of the application and it is instantiated when an `Esmerald`
application is created and the parameters are automatically provided.

### Enabling the scheduler

In order to make sure it does not always start, Esmerald is expecting a flag `enable_scheduler` to be True. Without
the `enable_scheduler = True`, the scheduler will not start.

The default behaviour is `enable_scheduler = False`.

```python hl_lines="10"
{!> ../docs_src/scheduler/scheduler.py !}
```

### Enabling the scheduler via settings

As mentioned in this documentation, Esmerald is unique with [settings](../application/settings.md) and therefore
the `enable_scheduler` can also be set to `True`/`False` there.

```python hl_lines="7"
{!> ../docs_src/scheduler/scheduler_settings.py !}
```

```shell
ESMERALD_SETTINGS_MODULE=AppSettings uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

!!! Tip
    Read more about how to take [advantage of the settings](../application/settings.md) and how to use them to leverage
    your application.

## Tasks

Tasks are simple pieces of functionality that contains the logic needed to run on a specific time.
Esmerald does not enforce any specific file name where the tasks should be, you can place them anywhere you want.

Once the tasks are created, you need to pass that same information to your Esmerald instance.

!!! tip
    There are more details about [how to create tasks](./handler.md) in the next section.

```python title="accounts/tasks.py"
{!> ../docs_src/scheduler/tasks/example1.py !}
```

There are two tasks created, the `collect_market_data` and `send_newsletter` which are placed inside a
`accounts/tasks`.

Now it is time to tell the application to activate the scheduler and run the tasks based on the settings provided
into the `scheduler` handler.

```python hl_lines="5-9"
{!> ../docs_src/scheduler/tasks/app_scheduler.py !}
```

**Or from the settings file**:

```python hl_lines="7 10-14"
{!> ../docs_src/scheduler/tasks/from_settings.py !}
```

Start the server with the newly created settings.

```shell
ESMERALD_SETTINGS_MODULE=AppSettings uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The `scheduler_tasks` is expecting a python dictionary where the both key and value are strings.

* `key` - The name of the task.
* `value` - Where the task is located.

!!! Warning
    Remember to activate the scheduler by enabling the `enable_scheduler` flag or else the scheduler will not
    start.
