from esmerald import Esmerald, Gateway, ORJSONResponse, Param, post
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create")
async def create_user(
    data: User,
    cookie: str = Param(cookie="csrftoken"),
) -> ORJSONResponse:
    """
    Run validations with the token header
    """
    ...


app = Esmerald(routes=Gateway(handler=create_user))
