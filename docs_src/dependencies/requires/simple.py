from typing import Any, Dict

from esmerald import Gateway, Requires, get, Esmerald


async def query_params(q: str | None = None, skip: int = 0, limit: int = 20):
    return {"q": q, "skip": skip, "limit": limit}


@get("/items")
async def get_params(params: Dict[str, Any] = Requires(query_params)) -> Any:
    return params


app = Esmerald(
    routes=[Gateway(handler=get_params)],
)
