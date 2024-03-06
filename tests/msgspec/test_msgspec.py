from typing import Union

import msgspec
from lilya import status
from pydantic import BaseModel
from typing_extensions import Annotated

from esmerald.datastructures.msgspec import Struct
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post
from esmerald.testclient import create_client


class User(Struct):
    name: str
    email: Union[str, None] = None


class BaseUser(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    user: User


@post(status_code=status.HTTP_202_ACCEPTED)
def get_user(payload: User) -> User:
    return payload


@post(status_code=status.HTTP_202_ACCEPTED)
def user(payload: BaseUser) -> User:
    return payload


def test_user_msgspec(test_client_factory):
    with create_client(routes=[Gateway(handler=get_user)]) as client:
        data = {"name": "Esmerald", "email": "esmerald@esmerald.dev"}
        response = client.post("/", json=data)

        assert response.json() == data


def test_user_msgspec_raise_validation_error(test_client_factory):
    with create_client(routes=[Gateway(handler=get_user)]) as client:
        data = {"name": 1, "email": "esmerald@esmerald.dev"}
        response = client.post("/", json=data)

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Validation failed for http://testserver/ with method POST.",
            "errors": [{"name": "Expected `str`, got `int`"}],
        }


def test_user_msgspec_two(test_client_factory):
    with create_client(routes=[Gateway(handler=user)]) as client:
        data = {"user": {"name": "Esmerald", "email": "esmerald@esmerald.dev"}}
        response = client.post("/", json=data)
        assert response.json() == data


Id = Annotated[int, msgspec.Meta(gt=0)]
Email = Annotated[str, msgspec.Meta(min_length=5, max_length=100, pattern="[^@]+@[^@]+\\.[^@]+")]


class Comment(msgspec.Struct):
    id: Id
    email: Email


@post(status_code=status.HTTP_202_ACCEPTED)
def comments(payload: Comment) -> Comment:
    return payload


def test_user_msgspec_constraints_name(test_client_factory):
    with create_client(routes=[Gateway(handler=comments)]) as client:
        data = {"id": -1, "email": "cenas"}
        response = client.post("/", json=data)

        assert response.status_code == 400
        assert response.json()["errors"] == [{"id": "Expected `int` >= 1"}]


def test_user_msgspec_constraints_email(test_client_factory):
    with create_client(routes=[Gateway(handler=comments)]) as client:
        data = {"id": 4, "email": "cenas"}
        response = client.post("/", json=data)

        assert response.status_code == 400
        assert response.json()["errors"] == [
            {"email": "Expected `str` matching regex '[^@]+@[^@]+\\\\.[^@]+'"}
        ]


class Address(msgspec.Struct):
    name: str


class AddressBook(msgspec.Struct):
    address: Address


@post()
def nested(payload: AddressBook) -> AddressBook:
    return payload


def test_nested_msgspec_struct(test_client_factory):
    with create_client(routes=[Gateway(handler=nested)]) as client:
        data = {"address": {"name": "Lisbon, Portugal"}}
        response = client.post("/", json=data)

        assert response.status_code == 201
        assert response.json() == {"address": {"name": "Lisbon, Portugal"}}
