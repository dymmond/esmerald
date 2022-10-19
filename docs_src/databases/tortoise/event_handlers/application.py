from configs.database.settings import TORTOISE_ORM

from esmerald import Esmerald
from esmerald.contrib.databases.tortoise import init_database, stop_database


async def start_database():
    await init_database(config=TORTOISE_ORM)


async def close_database():
    await stop_database()


app = Esmerald(on_startup=[start_database], on_shutdown=[close_database])
