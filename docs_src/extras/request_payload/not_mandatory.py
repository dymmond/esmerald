from typing import Optional

from pydantic import BaseModel, EmailStr

from esmerald import Esmerald, Gateway, post


class Address(BaseModel):
    zip_code: str
    country: str
    street: Optional[str]
    region: Optional[str]


class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[Address]


@post("/create")
async def create_user(payload: User) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
