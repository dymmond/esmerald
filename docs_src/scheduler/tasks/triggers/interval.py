from ravyn.contrib.schedulers.asyncz.decorator import scheduler
from asyncz.triggers import IntervalTrigger


@scheduler(trigger=IntervalTrigger(minutes=5))
def print_message():
    print("Hello, world!")


@scheduler(trigger=IntervalTrigger(hours=2))
def print_another_message():
    print("Hello, another world!")


@scheduler(
    trigger=IntervalTrigger(hours=2, start_at="2022-01-01 09:30:00", end_at="2023-01-01 11:00:00")
)
def from_interval():
    print("Hello, from crontab!")
