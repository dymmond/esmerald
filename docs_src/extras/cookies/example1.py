from pydantic import BaseModel, EmailStr

from ravyn import Cookie, Ravyn, Gateway, JSONResponse, post


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create")
async def create_user(
    data: User,
    cookie: str = Cookie(value="csrftoken"),
) -> JSONResponse:
    """
    Run validations with the token header
    """
    ...


app = Ravyn(routes=Gateway(handler=create_user))
