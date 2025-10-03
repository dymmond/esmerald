from pydantic import EmailStr

from ravyn.conf import settings
from ravyn.contrib.auth.mongoz.base_user import User as BaseUser

registry = settings.registry


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    class Meta:
        registry = registry
        database = "my_db"

    def __str__(self):
        return f"{self.email} - {self.last_login}"


async def create_user(
    first_name: str, last_name: str, username: str, email: EmailStr, password: str
) -> User:
    """
    Creates a user in the database.
    """
    user = await User.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    return user
