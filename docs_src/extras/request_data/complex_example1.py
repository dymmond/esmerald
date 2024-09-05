from pydantic import BaseModel, EmailStr

from esmerald import Esmerald, Gateway, post


class User(BaseModel):
    name: str
    email: EmailStr


class Address(BaseModel):
    street_name: str
    post_code: str


@post("/create")
async def create_user(user: User, address: Address) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
