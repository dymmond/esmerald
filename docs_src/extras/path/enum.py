from enum import Enum

from esmerald import Esmerald, Gateway, JSONResponse, get


class UserEnum(Enum):
    user = "user"
    admin = "admin"


@get("/users/{user_type}")
async def read_user(user_type: UserEnum) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
