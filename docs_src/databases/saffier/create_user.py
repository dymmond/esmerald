from pydantic import EmailStr

from esmerald.conf import settings
from esmerald.contrib.auth.saffier.base_user import User as BaseUser

database, models = settings.registry


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    class Meta:
        registry = models

    def __str__(self):
        return f"{self.email} - {self.last_login}"


async def create_user(
    first_name: str, last_name: str, username: str, email: EmailStr, password: str
) -> User:
    """
    Creates a user in the database.
    """
    user = await User.query.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    return user
