from typing import Dict, Union

from esmerald import Esmerald, EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    enable_scheduler: bool = True

    @property
    def scheduler_tasks(self) -> Dict[str, str]:
        ...

    @property
    def scheduler_configurations(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return (
            {
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
