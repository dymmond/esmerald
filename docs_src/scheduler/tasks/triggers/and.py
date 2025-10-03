from asyncz.triggers import AndTrigger, CronTrigger, IntervalTrigger
from ravyn.contrib.schedulers.asyncz.decorator import scheduler


@scheduler(trigger=AndTrigger([IntervalTrigger(hours=2), CronTrigger(day_of_week="sat,sun")]))
def print_message():
    print("Hello, world!")
