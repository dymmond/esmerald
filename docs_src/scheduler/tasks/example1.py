import logging

from asyncz.triggers import IntervalTrigger
from esmerald import scheduler
from loguru import logger

logging.basicConfig()
logging.getLogger("esmerald").setLevel(logging.DEBUG)


@scheduler(name="collect_data", trigger=IntervalTrigger(hours=12), max_intances=3)
def collect_market_data():
    logger.error("Collecting market data")
    ...


@scheduler(
    name="send_email_newsletter",
    trigger=IntervalTrigger(days=7),
    max_intances=3,
)
def send_newsletter():
    logger.warning("sending email newsletter!")
    ...
