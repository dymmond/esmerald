from pydantic import EmailStr
from edgy import monkay


# Update password
async def set_password(email: EmailStr, password: str) -> None:
    """
    Set the password of a user is correct.
    """
    registry = monkay.instance.registry
    async with registry:
        User = registry.get_model("User")
        user: User = await User.query.get(email=email)

        await user.set_password(password)
