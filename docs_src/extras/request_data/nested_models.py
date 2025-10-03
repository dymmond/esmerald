from pydantic import BaseModel, EmailStr

from ravyn import Ravyn, Gateway, post


class Address(BaseModel):
    zip_code: str
    country: str
    street: str
    region: str


class User(BaseModel):
    name: str
    email: EmailStr
    address: Address


@post("/create")
async def create_user(data: User) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Ravyn(routes=[Gateway(handler=create_user)])
