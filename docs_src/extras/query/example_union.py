from typing import Union

from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, q: Union[int, None] = None) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
