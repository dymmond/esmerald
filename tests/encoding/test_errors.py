from typing import Any

from attrs import define, field, has

from esmerald import Gateway, post
from esmerald.encoders import Encoder, register_esmerald_encoder
from esmerald.testclient import create_client


class AttrsEncoder(Encoder):

    def is_type(self, value: Any) -> bool:
        return has(value)


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
        assert response.status_code == 400
        assert (
            response.json()["errors"][0] == "All Esmerald encoders must implement encode() method."
        )
