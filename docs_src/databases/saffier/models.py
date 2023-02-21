from enum import Enum

from esmerald.contrib.auth.saffier.base_user import User as BaseUser
from saffier import Database, Registry, fields

database = Database("<YOUR-SQL-QUERY_STRING")
models = Registry(database=database)


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
    role = fields.ChoiceField(
        UserType,
        max_length=255,
        null=False,
        default=UserType.USER,
    )

    class Meta:
        registry = models

    def __str__(self):
        return f"{self.email} - {self.role}"


# Create the db and tables
# Don't use this in production! Use Alembic or any tool to manage
# The migrations for you
await models.create_all()

await User.query.create(is_active=False)

user = await User.query.get(id=1)
print(user)
# User(id=1)
