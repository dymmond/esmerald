from typing import Union

from lilya import status

from esmerald import Response
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


@get("/three", status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_three() -> Response:
    return Response("Ok", status_code=status.HTTP_103_EARLY_HINTS)


@get("/four")
def route_four() -> Response:
    return Response("Ok")


@get("/five", status_code=status.HTTP_207_MULTI_STATUS)
def route_five() -> Response:
    return Response("Ok")


def test_ujson_response(test_client_factory):
    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/one")

        assert response.json() == {"test": 1}


def test_ujson_orjson(test_client_factory):
    with create_client(routes=[Gateway(handler=route_two)]) as client:
        response = client.get("/two")

        assert response.json() == {"test": 2}


def test_override(test_client_factory):
    with create_client(routes=[Gateway(handler=route_three)]) as client:
        response = client.get("/three")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_103_EARLY_HINTS


def test_default(test_client_factory):
    with create_client(routes=[Gateway(handler=route_four)]) as client:
        response = client.get("/four")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_200_OK


def test_default_decorator(test_client_factory):
    with create_client(routes=[Gateway(handler=route_five)]) as client:
        response = client.get("/five")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_207_MULTI_STATUS


@get(status_code=status.HTTP_207_MULTI_STATUS)
def multiple(name: Union[str, None]) -> Response:
    if name is None:
        return Response("Ok")
    if name == "test":
        return Response("Ok", status_code=status.HTTP_401_UNAUTHORIZED)
    if name == "esmerald":
        return Response("Ok", status_code=status.HTTP_300_MULTIPLE_CHOICES)
    return Response("Ok")


def test_multiple(test_client_factory):
    with create_client(
        routes=[
            Gateway(path="/multi", handler=multiple),
            Gateway(path="/multi/{name}", handler=multiple),
        ]
    ) as client:
        response = client.get("/multi")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_207_MULTI_STATUS

        response = client.get("/multi/test")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.get("/multi/esmerald")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_300_MULTIPLE_CHOICES

        response = client.get("/multi/other")

        assert response.text == "Ok"
        assert response.status_code == status.HTTP_207_MULTI_STATUS
