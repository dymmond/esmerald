from typing import Tuple

from functools import cached_property
from edgy import Registry

from esmerald.conf.global_settings import EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    # this strategy works only when there is a single set of models (no clashing model names, no redefinitions)
    # otherwise have a look in esmerald tests how it is solved
    @cached_property
    def registry(self) -> Registry:
        return Registry("<YOUR-SQL-QUERY-STRING")
