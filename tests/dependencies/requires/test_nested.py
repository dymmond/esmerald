from typing import Any, Dict

from esmerald import Gateway, Requires, get
from esmerald.testclient import create_client


async def query_params(q: str | None = None, skip: int = 0, limit: int = 20):
    return {"q": q, "skip": skip, "limit": limit}


async def get_user() -> Dict[str, Any]:
    return {"username": "admin"}


async def get_user(
    user: Dict[str, Any] = Requires(get_user), params: Dict[str, Any] = Requires(query_params)
):
    return {"user": user, "params": params}


@get("/info")
async def get_params(info: Dict[str, Any] = Requires(get_user)) -> Any:
    return info


def test_simple(test_client_factory):
    with create_client(routes=[Gateway(handler=get_params)]) as client:
        response = client.get("/info")

        assert response.json() == {
            "user": {"username": "admin"},
            "params": {"q": None, "skip": 0, "limit": 20},
        }
