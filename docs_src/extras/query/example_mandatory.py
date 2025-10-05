from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users")
async def read_user(limit: int) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
