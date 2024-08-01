from typing import Optional

from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, q: Optional[int] = None) -> JSONResponse: ...


app = Esmerald(
    routes=[
        Gateway(read_user),
    ]
)
