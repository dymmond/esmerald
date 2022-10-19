from datetime import date

from esmerald import scheduler
from esmerald.schedulers.apscheduler.triggers import DateTrigger


def print_text(text):
    print(text)


@scheduler(trigger=DateTrigger(run_date=date(2022, 11, 6), args=["text"]))
def print_message():
    print_text("Hello, world!")


@scheduler(trigger=DateTrigger(run_date="2022-11-06 14:30:00", args=["text"]))
def print_another_message():
    print_text("Hello, another world!")
