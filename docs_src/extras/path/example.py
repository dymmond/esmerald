from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users/{user_id}")
async def read_user(user_id: str) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
