from typing import Any, Optional

from pydantic import BaseModel

from esmerald import Gateway, post
from esmerald.testclient import create_client


class User(BaseModel):
    username: str


@post("/optional")
async def create(data: Optional[User]) -> Any:
    return data if data else {}


def test_optional():
    with create_client(routes=[Gateway(handler=create)]) as client:
        response = client.post("/optional", json={"username": "test"})
        assert response.status_code == 201
        assert response.json() == {"username": "test"}

        response = client.post("/optional", json={})
        assert response.status_code == 201
        assert response.json() == {}

        response = client.post("/optional")
        assert response.status_code == 201
        assert response.json() == {}


@post("/union")
async def create_union(data: Optional[User]) -> Any:
    return data if data else {}


def test_union():
    with create_client(routes=[Gateway(handler=create_union)]) as client:
        response = client.post("/union", json={"username": "test"})
        assert response.status_code == 201
        assert response.json() == {"username": "test"}

        response = client.post("/union", json={})
        assert response.status_code == 201
        assert response.json() == {}

        response = client.post("/union")
        assert response.status_code == 201
        assert response.json() == {}
