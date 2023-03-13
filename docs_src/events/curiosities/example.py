from contextlib import asynccontextmanager

from saffier import Database, Registry

database = Database("postgresql+asyncpg://user:password@host:port/database")
registry = Registry(database=database)


@asynccontextmanager
async def custom_context_manager():
    await database.connect()
    yield
    await database.disconnect()


async with custom_context_manager() as async_context:
    # Do something here
    ...
