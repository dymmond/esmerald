from typing import Union

from esmerald.schedulers.apscheduler.triggers import (
    AndTrigger,
    BaseCombiningTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
)

TriggerHandler = Union[
    AndTrigger,
    BaseCombiningTrigger,
    CronTrigger,
    DateTrigger,
    IntervalTrigger,
    OrTrigger,
]

TriggerType = Union[str, TriggerHandler]
