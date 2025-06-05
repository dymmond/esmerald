from asyncz.executors import AsyncIOExecutor, ThreadPoolExecutor
from asyncz.stores.mongo import MongoDBStore
from esmerald import EsmeraldSettings
from esmerald.contrib.schedulers import SchedulerConfig
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig


class CustomSettings(EsmeraldSettings):
    @property
    def scheduler_config(self) -> SchedulerConfig:
        stores = {"default": MongoDBStore()}

        # Define the executors
        # Override the default ot be the AsyncIOExecutor
        executors = {
            "default": AsyncIOExecutor(),
            "threadpool": ThreadPoolExecutor(max_workers=20),
        }

        # Set the defaults
        task_defaults = {"coalesce": False, "max_instances": 4}

        return AsynczConfig(
            tasks=...,
            timezone="UTC",
            stores=stores,
            executors=executors,
            task_defaults=task_defaults,
        )
