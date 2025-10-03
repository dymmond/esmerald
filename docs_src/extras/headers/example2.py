from pydantic import BaseModel, EmailStr

from ravyn import Ravyn, Gateway, JSONResponse, Param, post


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create")
async def create_user(
    data: User,
    token: str = Param(header="X-API-TOKEN"),
) -> JSONResponse:
    """
    Run validations with the token header
    """
    ...


app = Ravyn(routes=Gateway(handler=create_user))
