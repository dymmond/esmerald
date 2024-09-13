from typing import List, Optional, Union

from typing_extensions import Annotated

from esmerald import Gateway, JSONResponse, Query, get
from esmerald.testclient import create_client


@get("/list")
async def check_list(a_value: List[str]) -> JSONResponse:
    return JSONResponse({"value": a_value})


@get("/another-list")
async def check_another_list(
    a_value: Annotated[list, Query()] = ["true", "false", "test"]  # noqa
) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param(test_client_factory):
    with create_client(
        routes=[Gateway(handler=check_list), Gateway(handler=check_another_list)]
    ) as client:

        response = client.get("/list?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}

        response = client.get("/another-list?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/union")
async def union_list(a_value: Union[List[str], None]) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_union(test_client_factory):
    with create_client(routes=[Gateway(handler=union_list)]) as client:

        response = client.get("/union")

        assert response.status_code == 200
        assert response.json() == {"value": []}

        response = client.get("/union?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}


@get("/optional")
async def optional_list(a_value: Optional[List[str]]) -> JSONResponse:  # noqa
    return JSONResponse({"value": a_value})


def test_query_param_optional(test_client_factory):
    with create_client(routes=[Gateway(handler=optional_list)]) as client:

        response = client.get("/optional")

        assert response.status_code == 200
        assert response.json() == {"value": []}

        response = client.get("/optional?a_value=true&a_value=false&a_value=test")

        assert response.status_code == 200
        assert response.json() == {"value": ["true", "false", "test"]}
