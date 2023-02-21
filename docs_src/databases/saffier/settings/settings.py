from typing import Tuple

from esmerald.conf.global_settings import EsmeraldAPISettings
from saffier import Database, Registry


class AppSettings(EsmeraldAPISettings):
    @property
    def registry(self) -> Tuple[Database, Registry]:
        database = Database("<YOUR-SQL-QUERY-STRING")
        return database, Registry(database=database)
