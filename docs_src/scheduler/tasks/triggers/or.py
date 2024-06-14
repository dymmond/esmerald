from esmerald.contrib.schedulers.asyncz.decorator import scheduler
from asyncz.triggers import CronTrigger, OrTrigger


@scheduler(
    trigger=OrTrigger(
        [
            CronTrigger(day_of_week="mon", hour=2),
            CronTrigger(day_of_week="wed", hour=16),
        ]
    )
)
def print_message():
    print("Hello, world!")
