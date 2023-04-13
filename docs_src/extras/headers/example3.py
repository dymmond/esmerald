from pydantic import BaseModel, EmailStr

from esmerald import Esmerald, Gateway, Response, post
from esmerald.datastructures import ResponseHeader


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create", response_headers={"myauth": ResponseHeader(value="granted")})
async def create_user(data: User) -> Response:
    """
    Run validations with the token header
    """
    ...


app = Esmerald(routes=Gateway(handler=create_user))
