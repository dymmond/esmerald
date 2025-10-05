import pytest

from ravyn import Gateway, get, status
from ravyn.core.datastructures import JSON
from ravyn.core.datastructures.encoders import ORJSON, UJSON
from ravyn.testclient import create_client


@pytest.mark.parametrize("response", [JSON, ORJSON, UJSON])
def test_json_datastructure(response, test_client_factory):
    @get()
    async def home() -> response:
        return response(content={"detail": "using JSON structure"})

    with create_client(routes=[Gateway(handler=home)]) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["detail"] == "using JSON structure"


@pytest.mark.parametrize("response", [JSON, ORJSON, UJSON])
def test_json_datastructure_with_different_status_code(response, test_client_factory):
    @get()
    async def home_two() -> response:
        return response(content={"detail": "using JSON structure"}, status_code=201)

    with create_client(routes=[Gateway(handler=home_two)]) as client:
        response = client.get("/")

        assert response.status_code == 201
        assert response.json()["detail"] == "using JSON structure"


@pytest.mark.parametrize("response", [JSON, ORJSON, UJSON])
def test_json_datastructure_with_different_status_code_on_handler(response, test_client_factory):
    @get(status_code=status.HTTP_202_ACCEPTED)
    async def home_three() -> response:
        return response(content={"detail": "using JSON structure"})

    with create_client(routes=[Gateway(handler=home_three)]) as client:
        response = client.get("/")

        assert response.status_code == 202
        assert response.json()["detail"] == "using JSON structure"


@pytest.mark.parametrize("response", [JSON, ORJSON, UJSON])
def test_json_datastructure_with_different_status_code_on_handler_two(
    response, test_client_factory
):
    @get(status_code=status.HTTP_202_ACCEPTED)
    async def home_three() -> response:
        return response(content={"detail": "using JSON structure"}, status_code=201)

    with create_client(routes=[Gateway(handler=home_three)]) as client:
        response = client.get("/")

        assert response.status_code == 201
        assert response.json()["detail"] == "using JSON structure"
