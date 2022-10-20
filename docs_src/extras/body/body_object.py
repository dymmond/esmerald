from esmerald import Body, Esmerald, Gateway, post
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post("/create")
async def create_user(
    data: User = Body(title="Create User", description="Creates a new user in the system")
) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])
