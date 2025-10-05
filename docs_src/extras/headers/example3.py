from pydantic import BaseModel, EmailStr

from ravyn import Ravyn, Gateway, Response, post
from ravyn.core.datastructures import ResponseHeader


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create", response_headers={"myauth": ResponseHeader(value="granted")})
async def create_user(data: User) -> Response:
    """
    Run validations with the token header
    """
    ...


app = Ravyn(routes=Gateway(handler=create_user))
