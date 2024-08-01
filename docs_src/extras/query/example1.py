from esmerald import Esmerald, Gateway, JSONResponse, get

fake_users = [{"last_name": "Doe", "email": "john.doe@example.com"}]


@get("/users")
async def read_user(skip: int = 1, limit: int = 5) -> JSONResponse:
    return fake_users[skip : skip + limit]


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
