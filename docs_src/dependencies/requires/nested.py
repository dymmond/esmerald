from typing import Dict, Any
from esmerald import Gateway, Requires, get, Esmerald


async def query_params(q: str | None = None, skip: int = 0, limit: int = 20):
    return {"q": q, "skip": skip, "limit": limit}


async def get_user() -> Dict[str, Any]:
    return {"username": "admin"}


async def get_user(
    user: Dict[str, Any] = Requires(get_user), params: Dict[str, Any] = Requires(query_params)
):
    return {"user": user, "params": params}


@get("/info")
async def get_info(info: Dict[str, Any] = Requires(get_user)) -> Any:
    return info


app = Esmerald(
    routes=[Gateway(handler=get_info)],
)
