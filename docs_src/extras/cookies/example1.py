from esmerald import Cookie, Esmerald, Gateway, ORJSONResponse, post
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create")
async def create_user(
    data: User,
    cookie: str = Cookie(value="csrftoken"),
) -> ORJSONResponse:
    """
    Run validations with the token header
    """
    ...


app = Esmerald(routes=Gateway(handler=create_user))
