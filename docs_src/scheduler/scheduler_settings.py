from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.schedulers import AsyncIOScheduler
from esmerald.types import SchedulerType


class AppSettings(EsmeraldAPISettings):
    # It is already the default of EsmeraldAPISettings
    scheduler_class: SchedulerType = AsyncIOScheduler
    # default is False
    enable_scheduler: bool = True


app = Esmerald(routes=[...])
