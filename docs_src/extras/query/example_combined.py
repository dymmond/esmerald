from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}/{last_name}")
async def read_user(id: int, last_name: str, skip: int = 1, limit: int = 5) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
