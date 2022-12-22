from asyncz.triggers import CronTrigger, OrTrigger
from esmerald import scheduler


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
