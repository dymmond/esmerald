from typing import Union

from lilya import status

from esmerald import Response
from esmerald.enums import MediaType
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


@get("/six")
def route_six() -> bytes:
    return b"Ok"


@get("/seven")
def route_seven() -> str:
    return ""


@get("/eight")
def route_eight() -> str:
    return "hello"


@get("/nine")
def route_nine() -> None:
    pass


@get("/ten", media_type=MediaType.TEXT)
def route_ten() -> str:
    return "hel\"'lo"


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


def test_implicit_bytes_returnal(test_client_factory):
    with create_client(routes=[route_six]) as client:
        response = client.get("/six")

        assert response.text == "Ok"


def test_implicit_empty_str_returnal(test_client_factory):
    with create_client(routes=[route_seven]) as client:
        response = client.get("/seven")

        assert response.text == '""'


def test_str_returnal(test_client_factory):
    with create_client(routes=[route_eight]) as client:
        response = client.get("/eight")

        assert response.text == '"hello"'


def test_str_returnal_non_json(test_client_factory):
    with create_client(routes=[Gateway(handler=route_ten)]) as client:
        response = client.get("/ten")

        assert response.text == "hel\"'lo"


def test_implicit_none_returnal(test_client_factory):
    with create_client(routes=[route_nine]) as client:
        response = client.get("/nine")

        assert response.text == ""


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
