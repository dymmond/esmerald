from dataclasses import dataclass

import pytest
from pydantic.dataclasses import dataclass as pydantic_dataclass

from esmerald import ImproperlyConfigured
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
    def user(payload: UserIn) -> UserIn:
        return data

    data = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=user)])

    client = test_app_client_factory(app)
    response = client.post("/user", json=data)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}


def test_response_pydantic_dataclass(test_app_client_factory):
    @post(path="/another-user", status_code=200)
    def another_user(payload: UserOut) -> UserOut:
        return payload

    payload = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=another_user)])

    client = test_app_client_factory(app)
    response = client.post("/another-user", json=payload)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}


def test_raises_improperly_configured(test_app_client_factory):
    @post(path="/another-user", status_code=200)
    def another_user(payload: UserOut, data: UserOut) -> UserOut:
        return payload

    with pytest.raises(ImproperlyConfigured) as raised:
        Esmerald(routes=[Gateway(handler=another_user)])

    assert raised.value.args[0] == "500: Only 'data' or 'payload' must be provided but not both."
