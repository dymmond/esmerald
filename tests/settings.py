from typing import Optional, Tuple

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

    @property
    def registry(self) -> Tuple[Database, Registry]:
        database = Database("postgresql+asyncpg://postgres:postgres@localhost:5432/esmerald")
        return database, Registry(database=database)


class TestConfig(TestSettings):
    @property
    def scheduler_class(self) -> None:
        ...

    class Config:
        extra = "allow"
