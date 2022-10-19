from typing import Dict, Union

from esmerald import Esmerald, EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    enable_scheduler: bool = True

    @property
    def scheduler_tasks(self) -> Dict[str, str]:
        ...

    @property
    def scheduler_configurations(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "apscheduler.jobstores.mongo": {"type": "mongodb"},
            "apscheduler.jobstores.default": {
                "type": "sqlalchemy",
                "url": "sqlite:///jobs.sqlite",
            },
            "apscheduler.executors.default": {
                "class": "apscheduler.executors.pool:ThreadPoolExecutor",
                "max_workers": "20",
            },
            "apscheduler.executors.processpool": {
                "type": "processpool",
                "max_workers": "5",
            },
            "apscheduler.job_defaults.coalesce": "false",
            "apscheduler.job_defaults.max_instances": "3",
            "apscheduler.timezone": "UTC",
        }


app = Esmerald()
