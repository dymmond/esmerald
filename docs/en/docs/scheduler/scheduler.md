# Motivation

Almost every application in one way or another needs some sort of automated scheduler to run automated tasks.
In that in mind and with the help of the great widely used
<a href='https://asyncz.dymmond.com' target='_blank'>Asyncz</a>, Ravyn comes with a built-in
scheduler, saving you tons of headaches and simplifying the process of creating them.

## Requirements

Ravyn uses `asyncz` for this integration. You can install by running:

```shell
$ pip install ravyn[schedulers]
```

## AsynczConfig

The `AsynczConfig` is the main object that manages the internal scheduler of `Ravyn` with asyncz expecting:

* `scheduler_class` - An instance of the `Asyncz` schedule type. Passed via `scheduler_class`.

    <sup>Default: `AsyncIOScheduler`</sup>

* `tasks` - A python dictionary of both key, value string mapping the tasks. Passed via
`scheduler_tasks`.

    <sup>Default: `{}`</sup>

* `timezone` - The `timezone` of the scheduler. Passed via `timezone`.

    <sup>Default: `UTC`</sup>

* `configurations` - A python dictionary containing some extra configurations for the scheduler.
Passed via `scheduler_configurations`.
* `kwargs` - Any keyword argument that can be passed and injected into the `scheduler_class`.

Since `Ravyn` is an `ASGI` framework, it is already provided a default scheduler class that works alongside with
the application, the `AsyncIOScheduler`.

!!! Note
    This is for representation and explanation purposes as the RavynAPIExceptionScheduler cannot be instantiated,
    instead, expects parameters being sent upon creating an Ravyn application.

```python hl_lines="4"
from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(scheduler_config=AsynczConfig())
```

You can have your own scheduler config class as well, check the [SchedulerConfig](../configurations/scheduler.md#how-to-use-it)
for more information.

!!! warning
    Anything else that does not work with `AsyncIO` is very likely also not to work with Ravyn.

## AsynczConfig and the application

This is the default Ravyn integration with Asyncz and the class can be accessed via:

```python
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig
```

Because this is an Ravyn offer, you can always implement your own version if you don't like the way Ravyn handles
the Asyncz default integration and adapt to your own needs. This is thanks to the [SchedulerConfig](../configurations/scheduler.md#how-to-use-it)
from where AsynczConfig is derived.

### Enabling the scheduler

In order to make sure it does not always start, Ravyn is expecting a flag `enable_scheduler` to be True. Without
the `enable_scheduler = True`, the scheduler will not start.

The default behaviour is `enable_scheduler = False`.

```python hl_lines="10"
{!> ../../../docs_src/scheduler/scheduler.py !}
```

### Enabling the scheduler via settings

As mentioned in this documentation, Ravyn is unique with [settings](../application/settings.md) and therefore
the `enable_scheduler` can also be set to `True`/`False` there.

```python hl_lines="7"
{!> ../../../docs_src/scheduler/scheduler_settings.py !}
```

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

!!! Tip
    Read more about how to take [advantage of the settings](../application/settings.md) and how to use them to leverage
    your application.

## Tasks

Tasks are simple pieces of functionality that contains the logic needed to run on a specific time.
Ravyn does not enforce any specific file name where the tasks should be, you can place them anywhere you want.

Once the tasks are created, you need to pass that same information to your Ravyn instance.

!!! tip
    There are more details about [how to create tasks](./handler.md) in the next section.

```python title="accounts/tasks.py"
{!> ../../../docs_src/scheduler/tasks/example1.py !}
```

There are two tasks created, the `collect_market_data` and `send_newsletter` which are placed inside a
`accounts/tasks`.

Now it is time to tell the application to activate the scheduler and run the tasks based on the settings provided
into the `scheduler` handler.

```python hl_lines="6-10"
{!> ../../../docs_src/scheduler/tasks/app_scheduler.py !}
```

**Or from the settings file**:

```python hl_lines="6 10-14"
{!> ../../../docs_src/scheduler/tasks/from_settings.py !}
```

Start the server with the newly created settings.

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

The `scheduler_tasks` is expecting a python dictionary where the both key and value are strings.

* `key` - The name of the task.
* `value` - Where the task is located.

!!! Warning
    Remember to activate the scheduler by enabling the `enable_scheduler` flag or else the scheduler will not
    start.
