from typing import Any, Dict

from ravyn import Gateway, Requires, get, Ravyn


async def query_params(q: str | None = None, skip: int = 0, limit: int = 20):
    return {"q": q, "skip": skip, "limit": limit}


@get("/items")
async def get_params(params: Dict[str, Any] = Requires(query_params)) -> Any:
    return params


app = Ravyn(
    routes=[Gateway(handler=get_params)],
)
