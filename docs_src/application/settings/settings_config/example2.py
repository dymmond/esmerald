from typing import TYPE_CHECKING

from ravyn import Ravyn, RavynSettings
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig

if TYPE_CHECKING:
    from ravyn.types import SchedulerType


# Create a ChildRavynSettings object
class RavynSettings(RavynSettings):
    app_name: str = "my application"
    secret_key: str = "a child secret"

    @property
    def scheduler_config(self) -> AsynczConfig:
        return AsynczConfig()


# Create an Ravyn application
app = Ravyn(routes=..., settings_module=RavynSettings)
