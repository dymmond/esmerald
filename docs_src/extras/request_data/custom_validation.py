from typing import List

from esmerald import Esmerald, Gateway, post
from pydantic import BaseModel, EmailStr, Field, validator


class User(BaseModel):
    name: str
    email: EmailStr
    hobbies: List[str] = Field(min_items=3)
    age: int

    @validator("age", always=True)
    def validate_age(cls, value: int) -> int:
        """
        Validates the age of a user.
        """
        if value < 18:
            raise ValueError("The age must be at least 18.")
        return value

    @validator("name")
    def validate_age(cls, value: int) -> str:
        """
        Validates the name of a user.
        """
        if len(value) < 3:
            raise ValueError("The name must be at least 3 characters.")
        return value


@post("/create")
async def create_user(data: User) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
