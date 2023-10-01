from pydantic import EmailStr

from esmerald.conf import settings
from esmerald.contrib.auth.mongoz.base_user import User as BaseUser

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


# Update password
async def set_password(email: EmailStr, password: str) -> None:
    """
    Set the password of a user is correct.
    """
    user: User = await User.query.get(email=email)

    await user.set_password(password)
