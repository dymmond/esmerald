from typing import Union

from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, q: Union[int, None] = None) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
