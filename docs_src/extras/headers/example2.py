from esmerald import Esmerald, Gateway, ORJSONResponse, Param, post
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/create")
async def create_user(
    data: User,
    token: str = Param(value="X-API-TOKEN"),
) -> ORJSONResponse:
    """
    Run validations with the token header
    """
    ...


app = Esmerald(routes=Gateway(handler=create_user))
