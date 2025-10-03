from typing import List

from pydantic import BaseModel, EmailStr, Field

from ravyn import Ravyn, Gateway, post


class User(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    hobbies: List[str] = Field(min_items=3)
    age: int = Field(ge=18)


@post("/create")
async def create_user(payload: User) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Ravyn(routes=[Gateway(handler=create_user)])
