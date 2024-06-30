import logging

from loguru import logger

from asyncz.triggers import IntervalTrigger
from esmerald.contrib.schedulers.asyncz.decorator import scheduler

logging.basicConfig()
logging.getLogger("esmerald").setLevel(logging.DEBUG)


@scheduler(name="collect_data", trigger=IntervalTrigger(hours=12), max_instances=3)
def collect_market_data():
    logger.error("Collecting market data")
    ...


@scheduler(
    name="send_newsletter",
    trigger=IntervalTrigger(days=7),
    max_instances=3,
)
def send_newsletter():
    logger.warning("sending email newsletter!")
    ...
