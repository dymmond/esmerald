from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig


class AppSettings(EsmeraldAPISettings):
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


app = Esmerald(routes=[...])
