from asyncz.contrib.esmerald.decorator import scheduler
from asyncz.triggers import AndTrigger, CronTrigger, IntervalTrigger


@scheduler(trigger=AndTrigger([IntervalTrigger(hours=2), CronTrigger(day_of_week="sat,sun")]))
def print_message():
    print("Hello, world!")
