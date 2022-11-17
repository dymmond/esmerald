"""
Helpers for the TortoiseORM integragion.
"""
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Type, Union

from esmerald.conf import settings
from loguru import logger
from tortoise import Tortoise


async def init_database(
    config: Optional[dict] = None,
    config_file: Optional[str] = None,
    create_db: bool = False,
    db_url: Optional[str] = None,
    modules: Optional[Dict[str, Iterable[Union[str, ModuleType]]]] = None,
    use_tz: bool = False,
    timezone: str = "UTC",
    routers: Optional[List[Union[str, Type]]] = None,
) -> None:
    """
    Wrapper that establish a connection to the database.

    Example:
        from esmerald.contrib.tortoise import init_database
        from myapp.db import TORTOISE_ORM

        async def start_database():
            await init_database(config=TORTOISE_ORM)
    """
    logger.info("Starting database...")
    if not use_tz:
        use_tz = settings.use_tz
    if not timezone:
        timezone = settings.timezone
    await Tortoise.init(
        config=config,
        config_file=config_file,
        _create_db=create_db,
        db_url=db_url,
        modules=modules,
        use_tz=use_tz,
        timezone=timezone,
        routers=routers,
    )
    logger.info("Database started...")


async def stop_database() -> None:
    """
    Helper that stops the Tortoise Database.

    Example:
        from esmerald.contrib.tortoise import stop_database

        async def close_database():
            await stop_database()
    """
    logger.info("Closing connection to database")

    await Tortoise.close_connections()

    logger.info("Connection closed")
