from enum import Enum

from ravyn import Ravyn, Gateway, JSONResponse, get


class UserEnum(Enum):
    user = "user"
    admin = "admin"


@get("/users/{user_type}")
async def read_user(user_type: UserEnum) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
