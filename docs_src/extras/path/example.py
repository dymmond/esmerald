from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{user_id}")
async def read_user(user_id: str) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
