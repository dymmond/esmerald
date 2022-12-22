from typing import Union

from asyncz.triggers import (
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
