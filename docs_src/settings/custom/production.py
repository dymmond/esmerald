from typing import List

from esmerald.conf.enums import EnvironmentType
from esmerald.contrib.databases.tortoise import init_database, stop_database
from esmerald.types import LifeSpanHandler

from ..configs.production.databases import TORTOISE_ORM
from ..configs.settings import AppSettings


async def start_database():
    await init_database(config=TORTOISE_ORM)


async def close_database():
    await stop_database()


class ProductionSettings(AppSettings):
    # the environment can be names to whatever you want.
    environment: bool = EnvironmentType.TESTING
    debug: bool = True
    reload: bool = False

    @property
    def on_startup(self) -> List[LifeSpanHandler]:
        """
        List of events/actions to be done on_startup.
        """
        return [start_database]

    @property
    def on_shutdown(self) -> List[LifeSpanHandler]:
        """
        List of events/actions to be done on_shutdown.
        """
        return [close_database]
