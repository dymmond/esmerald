from typing import Dict, Union

import pytest
from pydantic import BaseModel

from esmerald import Gateway, get
from esmerald.exceptions import OpenAPIException
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.testclient import create_client


class Item(BaseModel):
    sku: Union[int, str]


async def test_invalid_response(test_client_factory):
    with pytest.raises(OpenAPIException) as raised:

        @get("/test", responses={"hello": {"description": "Not a valid response"}})
        def read_people() -> Dict[str, str]:
            return {"id": "foo"}

        with create_client(
            routes=[
                Gateway(handler=read_people),
            ]
        ) as client:
            client.get("/openapi.json")

    assert raised.value.detail == "An additional response must be an instance of OpenAPIResponse."


async def test_invalid_response_status(test_client_factory):
    with pytest.raises(OpenAPIException) as raised:

        @get("/test", responses={"hello": OpenAPIResponse(model=Item)})
        def read_people() -> Dict[str, str]:
            return {"id": "foo"}

        with create_client(
            routes=[
                Gateway(handler=read_people),
            ]
        ) as client:
            client.get("/openapi.json")

    assert raised.value.detail == "The status is not a valid OpenAPI status response."
