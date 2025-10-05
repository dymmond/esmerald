from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

app = Ravyn(
    routes=[...],
    enable_scheduler=True,
    scheduler_config=AsynczConfig(
        tasks={
            "collect_market_data": "accounts.tasks",
            "send_newsletter": "accounts.tasks",
        },
    ),
)
