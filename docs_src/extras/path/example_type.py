from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{user_id:int}")
async def read_user(user_id: int) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
