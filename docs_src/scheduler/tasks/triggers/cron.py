from asyncz.contrib.esmerald.decorator import scheduler
from asyncz.triggers import CronTrigger


@scheduler(trigger=CronTrigger(month="4-9,12", day="3rd friday", hour="0-4"))
def print_message():
    print("Hello, world!")


@scheduler(trigger=CronTrigger(day_of_week="mon-fri", hour=5, minute=30, end_at="2022-12-30"))
def print_another_message():
    print("Hello, another world!")


# From a crontab
@scheduler(trigger=CronTrigger.from_crontab("0 0 1-15 may-oct *"))
def from_crontab():
    print("Hello, from crontab!")
