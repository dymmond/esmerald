from mongoz import Registry

from esmerald.conf.global_settings import EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    @property
    def registry(self) -> Registry:
        database = "<YOUR-SQL-QUERY-STRING"
        return Registry(database)
