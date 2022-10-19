import time
from typing import Any, Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler as APSAsyncIOScheduler

# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command to execute>


def get_time():
    return time.strftime("%A, %d. %B %Y %I:%M:%S %p")


class AsyncIOScheduler(APSAsyncIOScheduler):
    def __init__(self, gconfig: Optional[Dict[Any, Any]] = None, **options):
        if not gconfig:
            gconfig = {}
        super().__init__(gconfig, **options)
