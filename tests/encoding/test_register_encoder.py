from collections import deque
from typing import Any

import pytest
from attrs import asdict, define, field, has

from esmerald import Esmerald, Gateway, post
from esmerald.encoders import ENCODER_TYPES_CTX, Encoder
from esmerald.testclient import EsmeraldTestClient, create_client


class AttrsEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return has(type(value))

    def is_type_structure(self, value: Any) -> bool:
        return has(value)

    def serialize(self, obj: Any) -> Any:
        return asdict(obj)

    def encode(self, annotation: Any, value: Any) -> Any:
        return annotation(**value)


@define
class AttrItem:
    name: str = field()
    age: int = field()
    email: str


@pytest.fixture(autouse=True, scope="function")
def additional_encoders():
    token = ENCODER_TYPES_CTX.set(deque(ENCODER_TYPES_CTX.get()))
    try:
        yield
    finally:
        ENCODER_TYPES_CTX.reset(token)


def test_can_parse_attrs(test_app_client_factory):
    @post("/create")
    async def create(data: AttrItem) -> AttrItem:
        assert type(ENCODER_TYPES_CTX.get()[0]) is AttrsEncoder
        return data

    app = Esmerald(routes=[Gateway(handler=create)], encoders=[AttrsEncoder])
    client = EsmeraldTestClient(app)

    response = client.post("/create", json={"name": "test", "age": 2, "email": "test@foobar.com"})
    assert response.status_code == 201
    assert response.json() == {"name": "test", "age": 2, "email": "test@foobar.com"}


def test_can_parse_attrs_errors(test_app_client_factory):
    @define
    class Item:
        sku: str = field()

        @sku.validator
        def check(self, attribute, value):
            if not isinstance(value, str):
                raise ValueError(f"'{attribute.name}' must be a string.")

    @post("/create")
    async def create(data: Item) -> AttrItem:
        assert type(ENCODER_TYPES_CTX.get()[0]) is AttrsEncoder
        return data

    with create_client(routes=[Gateway(handler=create)], encoders=[AttrsEncoder]) as client:
        response = client.post("/create", json={"sku": 1})
        assert response.status_code == 400
        assert response.json()["errors"] == ["'sku' must be a string."]
