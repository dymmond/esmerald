from typing import Union

from esmerald.schedulers.apscheduler.triggers import (
    AndTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
)

TriggerHandler = Union[
    AndTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
]

TriggerType = Union[str, TriggerHandler]
