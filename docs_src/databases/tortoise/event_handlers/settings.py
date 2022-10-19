from typing import List

from configs.database.settings import TORTOISE_ORM

from esmerald import EsmeraldAPISettings
from esmerald.contrib.databases.tortoise import init_database, stop_database
from esmerald.types import LifeSpanHandler


async def start_database():
    await init_database(config=TORTOISE_ORM)


async def close_database():
    await stop_database()


class AppSettings(EsmeraldAPISettings):
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
