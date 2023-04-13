from pydantic import EmailStr

from esmerald.contrib.auth.tortoise.base_user import User as BaseUser


class User(BaseUser):
    """
    Inherits from the BaseUser all the fields and adds extra unique ones.
    """

    def __str__(self):
        return f"{self.email} - {self.last_login}"


# Check if password is valid or correct
async def check_password(email: EmailStr, password: str) -> bool:
    """
    Check if the password of a user is correct.
    """
    user: User = await User.get(email=email)

    is_valid_password = await user.check_password(password)
    return is_valid_password
