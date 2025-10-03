from typing import Optional

from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, q: Optional[int] = None) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
