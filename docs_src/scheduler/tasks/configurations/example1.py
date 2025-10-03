import logging

from loguru import logger

from asyncz.triggers import IntervalTrigger
from ravyn.contrib.schedulers.asyncz.decorator import scheduler

logging.basicConfig()
logging.getLogger("ravyn").setLevel(logging.DEBUG)


@scheduler(
    name="collect_data",
    trigger=IntervalTrigger(hours=12),
    max_instances=3,
    store="mongo",
    executor="default",
)
def collect_market_data():
    logger.error("Collecting market data")
    ...


@scheduler(
    name="collect_data",
    trigger=IntervalTrigger(hours=12),
    max_instances=3,
    store="default",
    executor="processpoll",
)
def another_example():
    logger.error("Collecting market data")
    ...
