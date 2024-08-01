from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users/{user_id:int}")
async def read_user(user_id: int) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
