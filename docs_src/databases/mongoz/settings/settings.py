from mongoz import Registry

from esmerald.conf.global_settings import EsmeraldSettings


class AppSettings(EsmeraldSettings):
    @property
    def registry(self) -> Registry:
        database = "<YOUR-SQL-QUERY-STRING"
        return Registry(database)
