from dataclasses import dataclass

from pydantic.dataclasses import dataclass as pydantic_dataclass

from esmerald.applications import Esmerald
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post


@dataclass
class UserIn:
    name: str
    email: str


@pydantic_dataclass
class UserOut:
    name: str
    email: str


def test_response_dataclass(test_app_client_factory):
    @post(path="/user", status_code=200)
    def user(data: UserIn) -> UserIn:
        return data

    data = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=user)])

    client = test_app_client_factory(app)
    response = client.post("/user", json=data)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}


def test_response_pydantic_dataclass(test_app_client_factory):
    @post(path="/another-user", status_code=200)
    def another_user(data: UserOut) -> UserOut:
        return data

    data = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=another_user)])

    client = test_app_client_factory(app)
    response = client.post("/another-user", json=data)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}
