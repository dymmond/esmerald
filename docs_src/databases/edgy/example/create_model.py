from datetime import datetime
from enum import Enum

from edgy import Registry, fields

from ravyn.contrib.auth.edgy.base_user import User as BaseUser

models = Registry(database="sqlite:///db.sqlite")


class UserType(Enum):
    ADMIN = "admin"
    USER = "user"
    OTHER = "other"


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    date_of_birth: datetime = fields.DateField()
    is_verified: bool = fields.BooleanField(default=False)
    role: UserType = fields.ChoiceField(
        UserType,
        max_length=255,
        null=False,
        default=UserType.USER,
    )

    class Meta:
        registry = models

    def __str__(self):
        return f"{self.email} - {self.role}"
