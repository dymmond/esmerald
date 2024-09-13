from typing import Any, Dict, Optional, Union

from esmerald import Gateway, JSONResponse, get
from esmerald.testclient import create_client


@get("/dict")
async def check_dict(a_value: Dict[str, Any]) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param(test_client_factory):
    with create_client(routes=Gateway(handler=check_dict)) as client:
        response = client.get("/dict?a_value=true&b_value=false&c_value=test")

        assert response.status_code == 200
        assert response.json() == {
            "value": {"a_value": "true", "b_value": "false", "c_value": "test"}
        }


@get("/union")
async def union_dict(a_value: Union[Dict[str, Any], None]) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param_union(test_client_factory):
    with create_client(routes=Gateway(handler=union_dict)) as client:
        response = client.get("/union")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/union?a_value=true&b_value=false&c_value=test")

        assert response.status_code == 200
        assert response.json() == {
            "value": {"a_value": "true", "b_value": "false", "c_value": "test"}
        }


@get("/optional")
async def optional_dict(a_value: Optional[Dict[str, Any]]) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param_optional(test_client_factory):
    with create_client(routes=Gateway(handler=optional_dict)) as client:
        response = client.get("/optional")

        assert response.status_code == 200
        assert response.json() == {"value": None}

        response = client.get("/optional?a_value=true&b_value=false&c_value=test")

        assert response.status_code == 200
        assert response.json() == {
            "value": {"a_value": "true", "b_value": "false", "c_value": "test"}
        }
