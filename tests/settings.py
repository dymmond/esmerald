from functools import cached_property
from typing import Optional, Tuple

from edgy import Database as EdgyDatabase
from edgy import Registry as EdgyRegistry
from pydantic import ConfigDict
from saffier import Database, Registry

from esmerald.conf.global_settings import EsmeraldAPISettings


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
    def edgy_registry(self) -> Tuple[Database, Registry]:
        database = EdgyDatabase("postgresql+asyncpg://postgres:postgres@localhost:5432/esmerald")
        return database, EdgyRegistry(database=database)


class TestConfig(TestSettings):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def scheduler_class(self) -> None:
        """"""
