from datetime import datetime
from enum import Enum

import mongoz
from edgy import Registry

from esmerald.contrib.auth.edgy.base_user import User as BaseUser

database = "mongodb://localhost:27017"
registry = Registry(database)


class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"
    OTHER = "other"


class Role(mongoz.EmbeddedDocument):
    name: str = mongoz.String(max_length=255, default=UserType.USER)


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    date_of_birth: datetime = mongoz.Date()
    is_verified: bool = mongoz.Boolean(default=False)
    role: Role = mongoz.Embed(Role)

    class Meta:
        registry = registry
        database = "my_db"

    def __str__(self):
        return f"{self.email} - {self.role.name}"
