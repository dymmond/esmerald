from typing import Dict, Union

from msgspec import Struct
from pydantic import BaseModel

from esmerald import Gateway, Include, post
from esmerald.testclient import create_client


class PydanticItem(BaseModel):
    name: str


class MsgSpecItem(Struct):
    name: str


@post("/create", tags=["bar"])
async def create(pydantic: PydanticItem, msgspec: Union[MsgSpecItem, None]) -> Dict[str, str]:
    if not msgspec:
        return {"pydantic": pydantic}
    return {"pydantic": pydantic, "msgspec": msgspec}


def test_test_complex_simple_api(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[Gateway(handler=create)],
            )
        ],
        enable_openapi=True,
    ) as client:
        data = {
            "pydantic": {"name": "foo"},
            "msgspec": {"name": "bar"},
        }
        response = client.post("/create", json=data)

        assert response.status_code == 201
        assert response.json() == {"pydantic": {"name": "foo"}, "msgspec": {"name": "bar"}}


def test_test_complex_simple_not_required_api(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[Gateway(handler=create)],
            )
        ],
        enable_openapi=True,
    ) as client:
        data = {
            "pydantic": {"name": "foo"},
        }
        response = client.post("/create", json=data)

        assert response.status_code == 201
        assert response.json() == {"pydantic": {"name": "foo"}}


@post("/item", tags=["bar"])
async def item(pydantic: PydanticItem, msgspec: MsgSpecItem) -> Dict[str, str]:
    if not msgspec:
        return {"pydantic": pydantic}
    return {"pydantic": pydantic, "msgspec": msgspec}


def test_test_complex_raises_error(test_app_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[Gateway(handler=item)],
            )
        ],
        enable_openapi=True,
    ) as client:
        data = {
            "pydantic": {"name": "foo"},
        }
        response = client.post("/item", json=data)

        assert response.status_code == 400
        assert response.json()["errors"] == ["Expected `object`, got `null`"]
