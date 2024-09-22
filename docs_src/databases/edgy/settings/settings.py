from typing import Tuple

from edgy import Registry

from esmerald.conf.global_settings import EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    @property
    def registry(self) -> Registry:
        return Registry("<YOUR-SQL-QUERY-STRING")
