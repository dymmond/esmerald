from typing import Tuple

from saffier import Database, Registry

from esmerald.conf.global_settings import EsmeraldAPISettings


class AppSettings(EsmeraldAPISettings):
    @property
    def registry(self) -> Tuple[Database, Registry]:
        database = Database("<YOUR-SQL-QUERY-STRING")
        return database, Registry(database=database)
