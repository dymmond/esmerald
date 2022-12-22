from esmerald import Esmerald

scheduler_configurations = (
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

app = Esmerald(
    enable_scheduler=True,
    scheduler_tasks=...,
    scheduler_configurations=scheduler_configurations,
)
