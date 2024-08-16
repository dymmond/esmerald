# Handler

Esmerald uses <a href='https://asyncz.tarsild.io' target='_blank'>Asyncz</a> to manage the
scheduler internally and therefore their documentation is also up to date.

The handler is the `scheduler` used to decorate a function that you want to process as a task.

## Requirements

Please check the [minimum requirements](./scheduler.md#requirements) to use this feature within
your project.

## The scheduler

This decorator does a lot of the magic containing all the information needed about a task and how it should be
performed internally.

**Parameters**:

* **name** - The name given to the task. Not the name of the function.

    <sup>Default: `None`</sup>

* **trigger** - An instance of a [trigger](#triggers).

    <sup>Default: `None`</sup>

* **id** - Explicit identifier (id) for the task.

    <sup>Default: `None`</sup>

* **misfire_grace_time** - The seconds after the designated runtime that the task is still allowed to be run.

    <sup>Default: `undefined`</sup>

* **coalesce** - Run once instead of many times if the scheduler determines that the task should be run more than once
in succession.

    <sup>Default: `undefined`</sup>

* **max_instances** - The maximum number of concurrently running instances allowed for this task.

    <sup>Default: `undefined`</sup>

* **next_run_time** - When to first run the task, regardless of the trigger.

    <sup>Default: `undefined`</sup>

* **store** - The alias of the [store](#stores-executors-and-other-configurations) to store the task in.

    <sup>Default: `None`</sup>

* **executor** - The  alias of the executor to run the task with.

    <sup>Default: `None`</sup>

* **replace_existing** - True to replace an existing task with the same `id`.

    <sup>Default: `None`</sup>

* **is_enabled** - If a task should run or be disabled and not being triggered by the task scheduler.

    <sup>Default: `True`</sup>

* **args** - The list of positional arguments to call func with.

    <sup>Default: `None`</sup>

* **kwargs** - The dict of keyword arguments to call func with.

    <sup>Default: `None`</sup>

To obtain the `undefined` type:

```python
from asyncz.typing import undefined
```

## Triggers

Esmerald comes with some pre-defined triggers ready to be used by the application.

The built-in trigger cover the majority of the needs of all users. However if that is not the case, there is always
the option to create a
<a href="https://asyncz.tarsild.io/triggers/#custom-trigger" target="_blank">custom</a>.

* `BaseTrigger` - The base of all triggers and it can be extended to create a
<a href="https://asyncz.tarsild.io/triggers/#basetrigger" target="_blank">custom</a>.
* `CronTrigger`
* `IntervalTrigger`
* `DateTrigger`
* `OrTrigger`
* `AndTrigger`

Importing the triggers:

```python
from asyncz.triggers import (
    AndTrigger,
    BaseTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
)
```

Or you can simply import directly from the `asyncz` library as it is fully compatible.

### CronTrigger

Triggers when current time matches all specified time constraits. Very similar to the way the UNIX cron works.

```shell
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
│ │ │ │ │                                   7 is also Sunday on some systems)
│ │ │ │ │
│ │ │ │ │
* * * * * <command to execute>
```

**Parameters**:

* **year** (*int*|*str*) – 4-digit year
* **month** (*int*|*str*) – Month (1-12)
* **day** (*int*|*str*) – Day of month (1-31)
* **week** (*int*|*str*) – ISO week (1-53)
* **day_of_week** (*int*|*str*) – Number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
* **hour** (*int*|*str*) – Hour (0-23)
* **minute** (*int*|*str*) – Minute (0-59)
* **second** (*int*|*str*) – Second (0-59)
* **start_date** (*datetime*|*str*) – Earliest possible date/time to trigger on (inclusive)
* **end_date** (*datetime*|*str*) – Latest possible date/time to trigger on (inclusive)
* **timezone** (*datetime*.*tzinfo*|*str*) – Time zone to use for the date/time calculations (defaults to scheduler timezone)
* **jitter** (*int*|*None*) – Delay the task execution by jitter seconds at most

```python
{!> ../../../docs_src/scheduler/tasks/triggers/cron.py !}
```

### IntervalTrigger

Triggers on specified intervals, starting on `start_date` if specified or `datetime.now()` + interval otherwise.

**Parameters**:

* **weeks** (*int*) - Number of weeks to wait.
* **days** (*int*) - Number of days to wait.
* **hours** (*int*) - Number of hours to wait.
* **minutes** (*int*) - Number of minutes to wait.
* **seconds** (*int*) - Number of seconds to wait.
* **start_date** (*datetime*|*str*) - Starting point for the interval calculation.
* **end_date** (*datetime*|*str*) – Latest possible date/time to trigger on
* **timezone** (*datetime*.*tzinfo*|*str*) – Time zone to use for the date/time calculations
* **jitter** (*int*|*None*) – Delay the task execution by jitter seconds at most

```python
{!> ../../../docs_src/scheduler/tasks/triggers/interval.py !}
```

### DateTrigger

Triggers once on the given datetime. If `run_date` is left empty, current time is used.

**Parameters**:

* **run_date** (*datetime*|*str*) – The date/time to run the task at.
* **timezone** (*datetime*.*tzinfo*|*str*) – Time zone for run_date if it doesn’t have one already.

```python
{!> ../../../docs_src/scheduler/tasks/triggers/date.py !}
```

### OrTrigger

Always returns the earliest next fire time produced by any of the given triggers.
The trigger is considered finished when all the given triggers have finished their schedules.

**Parameters**:

* **triggers** (*list*) – Triggers to combine.
* **jitter** (*int*|*None*) – Delay the task execution by jitter seconds at most.

```python
{!> ../../../docs_src/scheduler/tasks/triggers/or.py !}
```

### AndTrigger

Always returns the earliest next fire time that all the given triggers can agree on.
The trigger is considered to be finished when any of the given triggers has finished its schedule.

**Parameters**:

* **triggers** (*list*) – Triggers to combine.
* **jitter** (*int*|*None*) – Delay the task execution by jitter seconds at most.

```python
{!> ../../../docs_src/scheduler/tasks/triggers/and.py !}
```

!!! Note
    These triggers are the same as the `Asyncz` and we didn't want to break existing functionality.
    For more examples how to use even different approaches, check their great documentation.

## Stores, executors and other configurations

Using the scheduler also means access to a lot of extra possible configurations that can be added such as `stores`,
`executors` and any other extra configuration needed.

Esmerald allows to pass those configurations via application instantiation or via [settings](../application/settings.md).

### Via application instantiation

```python
{!> ../../../docs_src/scheduler/tasks/configurations/app.py !}
```

### Via application settings

```python
{!> ../../../docs_src/scheduler/tasks/configurations/settings.py !}
```

Start the application with the new settings.

=== "MacOS & Linux"

    ```shell
    ESMERALD_SETTINGS_MODULE=AppSettings uvicorn src:app --reload
    
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:ESMERALD_SETTINGS_MODULE="AppSettings"; uvicorn src:app --reload
    
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```


### Configurations and the handler

When creating a task and using the `scheduler` one of the parameters is the `store`.

From the [example](#via-application-instantiation) you have new task stores and executors and those can be passed:

```python hl_lines="15-16 27-28"
{!> ../../../docs_src/scheduler/tasks/configurations/example1.py !}
```

!!! Tip
    Have a look at the documentation from
    <a href="https://asyncz.tarsild.io" target="_blank">Asyncz</a> and learn more
    about what can be done and how can be done. All the parameters available in the Asyncz `add_task` are also
    available in the `@scheduler` handler in the same way.
