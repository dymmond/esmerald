from typing import Any

from attrs import asdict, define, field, has

from esmerald import Gateway, post
from esmerald.encoders import Encoder, register_esmerald_encoder
from esmerald.testclient import create_client


class AttrsEncoder(Encoder):

    def is_type(self, value: Any) -> bool:
        return has(value)

    def serialize(self, obj: Any) -> Any:
        return asdict(obj)

    def encode(self, annotation: Any, value: Any) -> Any:
        return annotation(**value)


register_esmerald_encoder(AttrsEncoder)


@define
class AttrItem:
    name: str = field()
    age: int = field()
    email: str


def test_can_parse_attrs(test_app_client_factory):

    @post("/create")
    async def create(data: AttrItem) -> AttrItem:
        return data

    with create_client(routes=[Gateway(handler=create)]) as client:
        response = client.post(
            "/create", json={"name": "test", "age": 2, "email": "test@foobar.com"}
        )
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
        return data

    with create_client(routes=[Gateway(handler=create)]) as client:
        response = client.post("/create", json={"sku": 1})
        assert response.status_code == 400
        assert response.json()["errors"] == ["'sku' must be a string."]
