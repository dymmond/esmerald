from mongoz import Registry

from ravyn.conf.global_settings import RavynSettings


class AppSettings(RavynSettings):
    @property
    def registry(self) -> Registry:
        database = "<YOUR-SQL-QUERY-STRING"
        return Registry(database)
