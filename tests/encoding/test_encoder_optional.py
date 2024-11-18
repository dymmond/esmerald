from typing import Any, Optional, Union

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
async def create_union(data: Union[User, None]) -> Any:
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


@post("/optional-one")
async def create_one(test: Optional[User]) -> Any:
    return test if test else {}


def test_optional_one():
    with create_client(routes=[Gateway(handler=create_one)]) as client:
        response = client.post("/optional-one", json={"test": {"username": "test"}})
        assert response.status_code == 201
        assert response.json() == {"username": "test"}

        response = client.post("/optional-one", json={})
        assert response.status_code == 201
        assert response.json() == {}

        response = client.post("/optional-one")
        assert response.status_code == 201
        assert response.json() == {}


@post("/union-one")
async def create_union_one(test: Union[User, None]) -> Any:
    return test if test else {}


def test_union_one():
    with create_client(routes=[Gateway(handler=create_union_one)]) as client:
        response = client.post("/union-one", json={"test": {"username": "test"}})
        assert response.status_code == 201
        assert response.json() == {"username": "test"}

        response = client.post("/union-one", json={})
        assert response.status_code == 201
        assert response.json() == {}

        response = client.post("/union-one")
        assert response.status_code == 201
        assert response.json() == {}
