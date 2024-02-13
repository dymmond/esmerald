from __future__ import annotations

from esmerald.conf.enums import EnvironmentType
from esmerald.types import LifeSpanHandler

from ..configs.settings import AppSettings


async def start_database(): ...


async def close_database(): ...


class TestingSettings(AppSettings):
    # the environment can be names to whatever you want.
    environment: bool = EnvironmentType.TESTING
    debug: bool = True
    reload: bool = False

    @property
    def on_startup(self) -> list[LifeSpanHandler]:
        """
        List of events/actions to be done on_startup.
        """
        return [start_database]

    @property
    def on_shutdown(self) -> list[LifeSpanHandler]:
        """
        List of events/actions to be done on_shutdown.
        """
        return [close_database]
