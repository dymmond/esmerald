from esmerald import Body, Esmerald, Gateway, Header, ORJSONResponse, post
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post(path="/{name_id}")
async def create_user(
    data: User = Body(),
    token: str = Header(header="X-API-TOKEN"),
) -> ORJSONResponse:
    return ORJSONResponse({"token": token, "user": data})


app = Esmerald(routes=Gateway(handler=create_user))
