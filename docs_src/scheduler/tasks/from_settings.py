from ravyn import Ravyn, RavynSettings
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig


class AppSettings(RavynSettings):
    enable_scheduler: bool = True

    @property
    def scheduler_config(self) -> AsynczConfig:
        return AsynczConfig(
            tasks={
                "collect_market_data": "accounts.tasks",
                "send_newsletter": "accounts.tasks",
            },
            stores=...,
            executors=...,
        )


app = Ravyn(routes=[...])
