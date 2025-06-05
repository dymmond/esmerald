from typing import TYPE_CHECKING

from functools import cached_property
from edgy import Registry

from esmerald.conf.global_settings import EsmeraldSettings

if TYPE_CHECKING:
    from edgy import EdgySettings


class AppSettings(EsmeraldSettings):
    # this strategy works only when there is a single set of models (no clashing model names, no redefinitions)
    # otherwise have a look in esmerald tests how it is solved
    @cached_property
    def registry(self) -> Registry:
        return Registry("<YOUR-SQL-QUERY-STRING")

    # optional, in case we want a centralized place
    @cached_property
    def edgy_settings(self) -> "EdgySettings":
        from edgy import EdgySettings

        return EdgySettings(preloads=["myproject.models"])
