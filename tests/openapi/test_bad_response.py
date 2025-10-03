from typing import Dict, Union

import pytest
from pydantic import BaseModel

from ravyn import Gateway, get
from ravyn.exceptions import OpenAPIException
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.testclient import create_client


class Item(BaseModel):
    sku: Union[int, str]


async def test_invalid_response(test_client_factory):
    with pytest.raises(OpenAPIException) as raised:

        @get("/test", responses={"hello": {"description": "Not a valid response"}})
        def read_people() -> Dict[str, str]:  # pragma: no cover
            ...

        with create_client(  # pragma: no cover
            routes=[
                Gateway(handler=read_people),
            ]
        ):
            """ """

    assert raised.value.detail == "An additional response must be an instance of OpenAPIResponse."


async def test_invalid_response_status(test_client_factory):
    with pytest.raises(OpenAPIException) as raised:

        @get("/test", responses={"hello": OpenAPIResponse(model=Item)})
        def read_people() -> Dict[str, str]:  # pragma: no cover
            ...

        with create_client(  # pragma: no cover
            routes=[
                Gateway(handler=read_people),
            ]
        ):
            """ """

    assert raised.value.detail == "The status is not a valid OpenAPI status response."
