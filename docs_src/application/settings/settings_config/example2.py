from typing import TYPE_CHECKING

from esmerald import Esmerald, EsmeraldSettings
from esmerald.contrib.schedulers.asyncz.config import AsynczConfig

if TYPE_CHECKING:
    from esmerald.types import SchedulerType


# Create a ChildEsmeraldSettings object
class EsmeraldSettings(EsmeraldSettings):
    app_name: str = "my application"
    secret_key: str = "a child secret"

    @property
    def scheduler_config(self) -> AsynczConfig:
        return AsynczConfig()


# Create an Esmerald application
app = Esmerald(routes=..., settings_module=EsmeraldSettings)
