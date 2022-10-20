from esmerald import Esmerald, Gateway, Response, post
from esmerald.datastructures import Cookie
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


@post(
    path="/create",
    response_cookies=[
        Cookie(
            key="csrf",
            value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
            max_age=3000,
            httponly=True,
        )
    ],
)
async def create_user(data: User) -> Response:
    """
    Run validations with the token header
    """
    ...


app = Esmerald(routes=Gateway(handler=create_user))
