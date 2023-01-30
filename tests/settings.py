from typing import Optional

from esmerald.conf.global_settings import EsmeraldAPISettings


class TestSettings(EsmeraldAPISettings):
    app_name: str = "test_client"
    debug: bool = True
    enable_sync_handlers: bool = True
    enable_openapi: bool = False
    environment: Optional[str] = "testing"
    redirect_slashes: bool = True
    include_in_schema: bool = False


class TestConfig(TestSettings):
    @property
    def scheduler_class(self) -> None:
        ...

    class Config:
        extra = "allow"
