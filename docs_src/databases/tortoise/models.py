from enum import Enum

from tortoise import fields
from tortoise.exceptions import ValidationError
from tortoise.validators import Validator

from esmerald.contrib.auth.tortoise.base_user import User as BaseUser


class EmptyValueValidator(Validator):
    """
    Validate whether a string can empty.
    """

    def __call__(self, value: str):
        if not value:
            raise ValidationError("Value can not be empty")


class UserType(Enum):
    ADMIN = "admin"
    USER = "user"
    OTHER = "other"


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    date_of_birth = fields.DateField()
    is_verified = fields.BooleanField(default=False)
    role = fields.CharField(
        max_length=255,
        null=False,
        validators=[EmptyValueValidator],
        default=UserType.USER,
    )

    def __str__(self):
        return f"{self.email} - {self.role}"
