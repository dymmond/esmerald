import asyncio
import os
from functools import cached_property
from typing import Optional, Tuple

import mongoz
from edgy import Database as EdgyDatabase, Registry as EdgyRegistry
from edgy.testclient import DatabaseTestClient as EdgyDatabaseTestClient
from pydantic import ConfigDict
from saffier import Database, Registry

from esmerald.conf.global_settings import EsmeraldAPISettings
from esmerald.config.jwt import JWTConfig

TEST_DATABASE_URL = os.environ.get("DATABASE_URI", "mongodb://root:mongoadmin@localhost:27017")


class TestSettings(EsmeraldAPISettings):
    app_name: str = "test_client"
    debug: bool = True
    enable_sync_handlers: bool = True
    enable_openapi: bool = False
    environment: Optional[str] = "testing"
    redirect_slashes: bool = True
    include_in_schema: bool = False

    @cached_property
    def registry(self) -> Tuple[Database, Registry]:
        database = Database("postgresql+asyncpg://postgres:postgres@localhost:5432/esmerald")
        return database, Registry(database=database)

    @cached_property
    def edgy_registry(self) -> Tuple[EdgyDatabase, EdgyRegistry]:
        database = EdgyDatabaseTestClient(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/esmerald_edgy",
            drop_database=False,
            use_existing=True,
        )
        return database, EdgyRegistry(database=database)

    @cached_property
    def mongoz_registry(self) -> mongoz.Registry:
        return mongoz.Registry(TEST_DATABASE_URL, event_loop=asyncio.get_running_loop)

    @property
    def jwt_config(self) -> JWTConfig:
        return JWTConfig(signing_key=self.secret_key)


class TestConfig(TestSettings):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def scheduler_config(self) -> None:
        """"""
