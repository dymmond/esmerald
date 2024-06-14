from contextlib import asynccontextmanager
from functools import lru_cache

from asyncz.executors import AsyncIOExecutor, ThreadPoolExecutor
from asyncz.stores.mongo import MongoDBStore
from esmerald import Esmerald
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig


@asynccontextmanager
async def lifespan(app: Esmerald):
    # What happens on startup
    await get_scheduler_config().start()
    yield
    # What happens on shutdown
    await get_scheduler_config().shutdown()


@lru_cache
def get_scheduler_config() -> AsynczConfig:
    # Define the stores
    # Override the default MemoryStore to become RedisStore where the db is 0
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


app = Esmerald(
    routes=[...],
    lifespan=lifespan,
    scheduler_config=get_scheduler_config(),
)
