from typing import Union

from esmerald import Esmerald, Gateway, JSONResponse, Query, get


@get("/users")
async def read_user(q: str = Query(max_length=10)) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
