from typing import Dict

from esmerald import Esmerald, EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    enable_scheduler: bool = True

    @property
    def scheduler_tasks(self) -> Dict[str, str]:
        return {
            "collect_market_data": "accounts.tasks",
            "send_newsletter": "accounts.tasks",
        }


app = Esmerald(routes=[...])
