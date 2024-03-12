from typing import TYPE_CHECKING

from asyncz.schedulers import AsyncIOScheduler

from esmerald import Esmerald, EsmeraldAPISettings

if TYPE_CHECKING:
    from esmerald.types import SchedulerType


# Create a ChildEsmeraldSettings object
class EsmeraldSettings(EsmeraldAPISettings):
    app_name: str = "my application"
    secret_key: str = "a child secret"

    @property
    def scheduler_class(self) -> "SchedulerType":
        return AsyncIOScheduler


# Create an Esmerald application
app = Esmerald(routes=..., settings_module=EsmeraldSettings)
