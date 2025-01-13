from typing import Any

from esmerald import Gateway, Inject, Injects, JSONResponse, Requires, get, Esmerald


async def get_user():
    return {"id": 1, "name": "Alice"}


async def get_current_user(user: Any = Requires(get_user)):
    return user


@get(
    "/items",
    dependencies={"current_user": Inject(get_current_user)},
)
async def get_items(current_user: Any = Injects()) -> JSONResponse:
    return JSONResponse({"message": "Hello", "user": current_user})


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
