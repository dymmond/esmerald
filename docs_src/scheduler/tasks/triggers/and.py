from esmerald import scheduler
from esmerald.schedulers.apscheduler.triggers import (
    AndTrigger,
    CronTrigger,
    IntervalTrigger,
)


@scheduler(trigger=AndTrigger([IntervalTrigger(hours=2), CronTrigger(day_of_week="sat,sun")]))
def print_message():
    print("Hello, world!")
