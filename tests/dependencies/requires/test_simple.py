from typing import Any, Dict, Union

from ravyn import Gateway, Requires, get
from ravyn.testclient import create_client


async def query_params(q: Union[str, None] = None, skip: int = 0, limit: int = 20):
    return {"q": q, "skip": skip, "limit": limit}


@get("/items")
async def get_params(params: Dict[str, Any] = Requires(query_params)) -> Any:
    return params


def test_simple(test_client_factory):
    with create_client(routes=[Gateway(handler=get_params)]) as client:
        response = client.get("/items")

        assert response.json() == {"q": None, "skip": 0, "limit": 20}
