from pydantic import BaseModel, EmailStr
from typing import Union

from ravyn import Ravyn, Gateway, post


class User(BaseModel):
    name: str
    email: EmailStr


class Address(BaseModel):
    street_name: str
    post_code: str


@post("/create")
async def create_user(user: User, address: Union[Address, None]) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201

    Union is used but it could also be `Optional`.
    """


app = Ravyn(routes=[Gateway(handler=create_user)])
