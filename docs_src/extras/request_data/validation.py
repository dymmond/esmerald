from typing import List

from esmerald import Esmerald, Gateway, post
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    hobbies: List[str] = Field(min_items=3)
    age: int = Field(ge=18)


@post("/create")
async def create_user(data: User) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
