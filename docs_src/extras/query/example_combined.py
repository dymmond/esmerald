from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users/{id}/{last_name}")
async def read_user(id: int, last_name: str, skip: int = 1, limit: int = 5) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
