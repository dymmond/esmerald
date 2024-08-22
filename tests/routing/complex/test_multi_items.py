from pydantic import BaseModel

from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post
from esmerald.testclient import create_client


class Item(BaseModel):
    name: str


class User(BaseModel):
    username: str


class All(BaseModel):
    item: Item
    user: User


@post(path="/create")
async def create(item: Item, user: User) -> All:
    return All(item=item, user=user)


def test_can_have_multiple(test_client_factory):
    with create_client(routes=[Gateway(handler=create)]) as client:
        response = client.post(
            "/create", json={"item": {"name": "item"}, "user": {"username": "user"}}
        )
        assert response.status_code == 201
        assert response.json() == {"item": {"name": "item"}, "user": {"username": "user"}}


@post(path="/default-create")
async def default_create(data: Item, user: User) -> All:
    return All(item=data, user=user)


def test_default_have_multiple_data(test_client_factory):
    with create_client(routes=[Gateway(handler=default_create)]) as client:
        response = client.post(
            "/default-create", json={"data": {"name": "item"}, "user": {"username": "user"}}
        )
        assert response.status_code == 201
        assert response.json() == {"item": {"name": "item"}, "user": {"username": "user"}}


@post(path="/default-create-payload")
async def default_create_payload(payload: Item, user: User) -> All:
    return All(item=payload, user=user)


def test_default_have_multiple_payload(test_client_factory):
    with create_client(routes=[Gateway(handler=default_create_payload)]) as client:
        response = client.post(
            "/default-create-payload",
            json={"payload": {"name": "item"}, "user": {"username": "user"}},
        )
        assert response.status_code == 201
        assert response.json() == {"item": {"name": "item"}, "user": {"username": "user"}}


@post(path="/normal")
async def normal(payload: Item) -> All:
    return payload


def test_normal_payload(test_client_factory):
    with create_client(routes=[Gateway(handler=normal)]) as client:
        response = client.post("/normal", json={"name": "item"})
        assert response.status_code == 201
        assert response.json() == {"name": "item"}
