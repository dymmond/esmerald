from datetime import date

from asyncz.contrib.esmerald.decorator import scheduler
from asyncz.triggers import DateTrigger


def print_text(text):
    print(text)


@scheduler(trigger=DateTrigger(run_at=date(2022, 11, 6), args=["text"]))
def print_message():
    print_text("Hello, world!")


@scheduler(trigger=DateTrigger(run_at="2022-11-06 14:30:00", args=["text"]))
def print_another_message():
    print_text("Hello, another world!")
