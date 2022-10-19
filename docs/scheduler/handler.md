# Handler

Esmerald uses <a href='https://apscheduler.readthedocs.io/en/3.x/' target='_blank'>APScheduler</a> to manage the
scheduler internally and therefore their documentation is also up to date.

The handler is the `scheduler` used to decorate a function that you want to process as a task.

## The scheduler

This decorator does a lot of the magic containing all the information needed about a task and how it should be
performed internally.

**Parameters**:

* **name** - The name given to the task. Not the name of the function.

    <sup>Default: `None`</sup>

* **trigger** - An instance of a [trigger](#triggers).

    <sup>Default: `None`</sup>

* **identifier** - Explicit identifier (id) for the job.

    <sup>Default: `None`</sup>

* **misfire_grace_time** - The seconds after the designated runtime that the job is still allowed to be run.

    <sup>Default: `undefined`</sup>

* **coalesce** - Run once instead of many times if the scheduler determines that the job should be run more than once
in succession.

    <sup>Default: `undefined`</sup>

* **max_intances** - The maximum number of concurrently running instances allowed for this
job.

    <sup>Default: `undefined`</sup>

* **next_run_time** - When to first run the job, regardless of the trigger.

    <sup>Default: `undefined`</sup>

* **jobstore** - The alias of the [job store](#job-stores) to store the job in.

    <sup>Default: `None`</sup>

* **executor** - The  alias of the executor to run the job with.

    <sup>Default: `None`</sup>

* **replace_existing** - True to replace an existing job with the same `id`.

    <sup>Default: `None`</sup>

* **is_enabled** - If a task should run or be disabled and not being triggered by the task scheduler.

    <sup>Default: `True`</sup>

* **args** - The list of positional arguments to call func with.

    <sup>Default: `None`</sup>

* **kwargs** - The dict of keyword arguments to call func with.

    <sup>Default: `None`</sup>

To obtain the `undefined` type:

```python
from apscheduler.util import undefined
```

## Triggers

Esmerald comes with some pre-defined triggers ready to be used by the application.

The built-in trigger cover the majority of the needs of all users. However if that is not the case, there is always
the option to create a
<a href="https://apscheduler.readthedocs.io/en/3.x/extending.html#custom-triggers" target="_blank">custom</a>.

* `BaseTrigger` - The base of all triggers and it can be extended to create a
<a href="https://apscheduler.readthedocs.io/en/3.x/extending.html#custom-triggers" target="_blank">custom</a>.
* `CronTrigger`
* `IntervalTrigger`
* `DateTrigger`
* `OrTrigger`
* `AndTrigger`

Importing the triggers:

```python
from esmerald.schedulers.apscheduler.triggers import (
    AndTrigger,
    BaseTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
)
```

Or you can simply import directly from the `apscheduler` library as it is fully compatible.

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
* **jitter** (*int*|*None*) – Delay the job execution by jitter seconds at most

### IntervalTrigger

Triggers on specified intervals, starting on `start_date` if specified or `datetime.now()` + interval otherwise.

**Parameters**:

* **weeks** (*int*) - Number of weeks to wait.
* **days** (*int*) - Number of days to wait.
* **hours** (*int*) - Number of hours to wait.
* **minutes** (*int*) - Number of minutes to wait.
* **seconds** (*int*) - Number of seconds to wait.
* **start_date** (*datetime*|*str*) - Starting point for the interval calculation.
* **end_date** (*datetime*|*str*) – latest possible date/time to trigger on
* **timezone** (*datetime*.*tzinfo*|*str*) – time zone to use for the date/time calculations
* **jitter** (*int*|*None*) – delay the job execution by jitter seconds at most

### DateTrigger

Triggers once on the given datetime. If `run_date` is left empty, current time is used.

**Parameters**:

* **run_date** (*datetime*|*str*) – The date/time to run the job at.
* **timezone** (*datetime*.*tzinfo*|*str*) – Time zone for run_date if it doesn’t have one already.

### OrTrigger

Always returns the earliest next fire time produced by any of the given triggers.
The trigger is considered finished when all the given triggers have finished their schedules.

**Parameters**:

* **triggers** (*list*) – Triggers to combine.
* **jitter** (*int*|*None*) – Delay the job execution by jitter seconds at most.

### AndTrigger

Always returns the earliest next fire time that all the given triggers can agree on.
The trigger is considered to be finished when any of the given triggers has finished its schedule.

**Parameters**:

* **triggers** (*list*) – Triggers to combine.
* **jitter** (*int*|*None*) – Delay the job execution by jitter seconds at most.


## Job stores
