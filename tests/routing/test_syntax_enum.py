from enum import Enum

from pydantic import __version__

from ravyn import Gateway, JSONResponse, get
from ravyn.testclient import create_client

pydantic_version = ".".join(__version__.split(".")[:2])


class ItemType(str, Enum):
    sold = "sold"
    bought = "bought"


@get("/item/<item_type>")
async def item(item_type: ItemType) -> JSONResponse:
    return JSONResponse({"item_type": item_type})


def test_syntax():
    with create_client(routes=[Gateway(handler=item)]) as client:
        response = client.get("/item/sold")
        assert response.json() == {"item_type": "sold"}


def test_syntax_fail():
    with create_client(routes=[Gateway(handler=item)]) as client:
        response = client.get("/item/test")

        assert response.status_code == 400

        assert response.json() == {
            "detail": "Validation failed for http://testserver/item/test with method GET.",
            "errors": [
                {
                    "type": "enum",
                    "loc": ["item_type"],
                    "msg": "Input should be 'sold' or 'bought'",
                    "input": "test",
                    "ctx": {"expected": "'sold' or 'bought'"},
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/enum",
                }
            ],
        }
