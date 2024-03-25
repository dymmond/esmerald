from lilya import status

from esmerald.responses.encoders import ORJSONResponse, UJSONResponse
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.testclient import create_client


@get("/one", status_code=status.HTTP_202_ACCEPTED)
def route_one() -> UJSONResponse:
    return UJSONResponse({"test": 1})


@get("/two", status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_two() -> ORJSONResponse:
    return ORJSONResponse({"test": 2})


def test_ujson_response(test_client_factory):
    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/one")

        assert response.json() == {"test": 1}


def test_ujson_orjson(test_client_factory):
    with create_client(routes=[Gateway(handler=route_two)]) as client:
        response = client.get("/two")

        assert response.json() == {"test": 2}
