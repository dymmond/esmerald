from esmerald import Esmerald

scheduler_configurations = {
    "apscheduler.jobstores.mongo": {"type": "mongodb"},
    "apscheduler.jobstores.default": {
        "type": "sqlalchemy",
        "url": "sqlite:///jobs.sqlite",
    },
    "apscheduler.executors.default": {
        "class": "apscheduler.executors.pool:ThreadPoolExecutor",
        "max_workers": "20",
    },
    "apscheduler.executors.processpool": {"type": "processpool", "max_workers": "5"},
    "apscheduler.job_defaults.coalesce": "false",
    "apscheduler.job_defaults.max_instances": "3",
    "apscheduler.timezone": "UTC",
}

app = Esmerald(
    enable_scheduler=True,
    scheduler_tasks=...,
    scheduler_configurations=scheduler_configurations,
)
