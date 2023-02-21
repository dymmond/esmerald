from accounts.models import User
from pydantic import BaseModel

from esmerald import post


class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    username: str


@post(tags=["user"])
async def create_user(data: UserIn) -> None:
    """
    Creates a user in the system and returns the default 201
    status code.
    """
    await User.query.create_user(
        first_name="Test",
        last_name="test",
        email="foo@bar.com",
        password="1234password",
        username="test",
    )
