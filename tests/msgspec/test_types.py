from typing import Dict, List

import msgspec

from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post
from esmerald.testclient import create_client


class Address(msgspec.Struct):
    name: str


class AddressBook(msgspec.Struct):
    address: Address


@post()
def nested(payload: List[AddressBook]) -> List[AddressBook]:
    return payload


def test_nested_msgspec_struct(test_client_factory):
    with create_client(routes=[Gateway(handler=nested)]) as client:
        data = [{"address": {"name": "Lisbon, Portugal"}}]
        response = client.post("/", json=data)

        assert response.status_code == 201
        assert response.json() == [{"address": {"name": "Lisbon, Portugal"}}]


def test_nested_msgspec_struct_raises_error(test_client_factory):
    with create_client(routes=[Gateway(handler=nested)]) as client:
        data = [{"address": {"name": 1}}]
        response = client.post("/", json=data)

        assert response.status_code == 400


@post()
def another(payload: Dict[str, AddressBook]) -> List[AddressBook]:
    return payload


def test_nested_msgspec_struct_dict(test_client_factory):
    with create_client(routes=[Gateway(handler=another)]) as client:
        data = {"address-book": {"address": {"name": "Lisbon, Portugal"}}}
        response = client.post("/", json=data)

        assert response.status_code == 201
        assert response.json() == {"address-book": {"address": {"name": "Lisbon, Portugal"}}}


def test_nested_msgspec_struct_dict_raises_error(test_client_factory):
    with create_client(routes=[Gateway(handler=another)]) as client:
        data = {"address-book": {"address": {"name": 1}}}
        response = client.post("/", json=data)

        assert response.status_code == 400


@post()
def another_nested(payload: List[Dict[str, AddressBook]]) -> List[AddressBook]:
    return payload


def test_nested_msgspec_struct_list_dict(test_client_factory):
    with create_client(routes=[Gateway(handler=another_nested)]) as client:
        data = [{"address-book": {"address": {"name": "Lisbon, Portugal"}}}]
        response = client.post("/", json=data)

        assert response.status_code == 201
        assert response.json() == [{"address-book": {"address": {"name": "Lisbon, Portugal"}}}]


def xtest_nested_msgspec_struct_list_dict_raises_error(test_client_factory):
    with create_client(routes=[Gateway(handler=another_nested)]) as client:
        data = {"address-book": {"address": {"name": 1}}}
        response = client.post("/", json=data)

        assert response.status_code == 400
