from esmerald import Esmerald
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig

app = Esmerald(
    routes=[...],
    enable_scheduler=True,
    scheduler_config=AsynczConfig(
        tasks={
            "collect_market_data": "accounts.tasks",
            "send_newsletter": "accounts.tasks",
        },
    ),
)
