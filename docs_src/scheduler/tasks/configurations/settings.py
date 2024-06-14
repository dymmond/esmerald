from typing import Dict, Union

from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig


class AppSettings(EsmeraldAPISettings):
    enable_scheduler: bool = True

    @property
    def scheduler_config(self) -> AsynczConfig:
        return AsynczConfig(
            tasks=...,
            configurations={
                "asyncz.stores.mongo": {"type": "mongodb"},
                "asyncz.stores.default": {"type": "redis", "database": "0"},
                "asyncz.executors.threadpool": {
                    "max_workers": "20",
                    "class": "asyncz.executors.threadpool:ThreadPoolExecutor",
                },
                "asyncz.executors.default": {"class": "asyncz.executors.asyncio::AsyncIOExecutor"},
                "asyncz.task_defaults.coalesce": "false",
                "asyncz.task_defaults.max_instances": "3",
                "asyncz.task_defaults.timezone": "UTC",
            },
        )


app = Esmerald()
