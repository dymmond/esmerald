from typing import Any

import pytest
from lilya.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from esmerald import Include, route, status
from esmerald.enums import HttpMethod
from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.gateways import Gateway
from esmerald.testclient import create_client


@pytest.mark.parametrize(
    "method, status_code",
    [
        (HttpMethod.POST.value, HTTP_201_CREATED),
        (HttpMethod.DELETE.value, HTTP_204_NO_CONTENT),
        (HttpMethod.GET.value, HTTP_200_OK),
        (HttpMethod.PUT.value, HTTP_200_OK),
        (HttpMethod.PATCH.value, HTTP_200_OK),
    ],
)
def test_route_handler_default_status_code(method: Any, status_code: int) -> None:
    @route(path="/", methods=[method], status_code=status_code)
    async def to_be_decorated() -> None: ...

    with create_client(routes=[Gateway(handler=to_be_decorated)]) as client:
        response = getattr(client, method.lower())("/")
        assert response.status_code == status_code


def test_raises_exception_route_http_handler() -> None:
    with pytest.raises(ImproperlyConfigured):
        route(path="/", status_code=status.HTTP_200_OK)


@pytest.mark.parametrize(
    "method",
    ["test", "bla", "guet", "poust", "git"],
)
def test_raises_exception_route_http_handler_on_invalid_method(method: str) -> None:
    with pytest.raises(ImproperlyConfigured):
        route(path="/", methods=[method])


def test_raises_exception_route_route_handler() -> None:
    with pytest.raises(ImproperlyConfigured):
        route(path="/", status_code=status.HTTP_200_OK)


@route(status_code=status.HTTP_202_ACCEPTED, methods=["GET", "POST"])
async def home() -> str:
    return "home"


@route("/alone", status_code=status.HTTP_202_ACCEPTED, methods=["GET"])
def alone() -> str:
    return "alone"


@route("/alone", status_code=status.HTTP_202_ACCEPTED, methods=["GET"])
def with_include(name: str) -> str:
    return name


def test_handler_route(test_client_factory):
    with create_client(
        routes=[
            Gateway("/home", handler=home),
            Gateway(handler=alone),
            Include("/try", routes=[Gateway("/{name}", handler=with_include)]),
        ]
    ) as client:
        response = client.get("/home")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == "home"

        response = client.post("/home")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == "home"

        response = client.get("/alone")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == "alone"

        response = client.get("/try/esmerald/alone")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == "esmerald"


def test_handler_route_two(test_client_factory):
    with create_client(
        routes=[
            Gateway("/home", handler=home),
        ]
    ) as client:
        response = client.delete("/home")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.json()["detail"] == "Method DELETE not allowed."
