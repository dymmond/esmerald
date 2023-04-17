import logging

from asyncz.contrib.esmerald.decorator import scheduler
from asyncz.triggers import IntervalTrigger
from loguru import logger

logging.basicConfig()
logging.getLogger("esmerald").setLevel(logging.DEBUG)


@scheduler(
    name="collect_data",
    trigger=IntervalTrigger(hours=12),
    max_intances=3,
    store="mongo",
    executor="default",
)
def collect_market_data():
    logger.error("Collecting market data")
    ...


@scheduler(
    name="collect_data",
    trigger=IntervalTrigger(hours=12),
    max_intances=3,
    store="default",
    executor="processpoll",
)
def another_example():
    logger.error("Collecting market data")
    ...
