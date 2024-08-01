from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users")
async def read_user(limit: int) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
