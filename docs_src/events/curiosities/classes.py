from saffier import Database, Registry

database = Database("postgresql+asyncpg://user:password@host:port/database")
registry = Registry(database=database)


class DatabaseContext:
    # Enter the async context manager
    async def __aenter__(self):
        await database.connect()

    # Exit the async context manager
    async def __aexit__(self):
        await database.disconnect()


async with DatabaseContext() as async_context:
    # Do something here
    ...
