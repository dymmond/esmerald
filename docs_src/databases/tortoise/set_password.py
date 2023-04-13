from pydantic import EmailStr

from esmerald.contrib.auth.tortoise.base_user import User as BaseUser


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    def __str__(self):
        return f"{self.email} - {self.last_login}"


# Update password
async def set_password(email: EmailStr, password: str) -> None:
    """
    Set the password of a user is correct.
    """
    user: User = await User.get(email=email)

    await user.set_password(password)
