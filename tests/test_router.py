from unittest import mock

import pytest
from lilya import status

from esmerald import ChildEsmerald
from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.routing.router import Include, Router
from esmerald.testclient import create_client


@get(status_code=status.HTTP_202_ACCEPTED)
def route_one() -> dict:
    return {"test": 1}


@get(status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_two() -> dict:
    return {"test": 2}


def test_add_router(test_client_factory) -> None:
    """
    Adds a route to the router.
    """

    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        router = Router(path="/aditional", routes=[Gateway("/second", handler=route_two)])
        client.app.add_router(router=router)

        response = client.get("/aditional/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT


def test_add_router_events(test_client_factory) -> None:
    """
    Adds a route to the router and events
    """

    def start(): ...

    def stop(): ...

    with create_client(
        routes=[Gateway(handler=route_one)], on_startup=[start], on_shutdown=[stop]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        router = Router(path="/aditional", routes=[Gateway("/second", handler=route_two)])
        client.app.add_router(router=router)

        response = client.get("/aditional/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        assert start in client.app.on_startup
        assert stop in client.app.on_shutdown


def test_add_router_with_includes(test_client_factory) -> None:
    """
    Adds a route to the router with includes.
    """

    with create_client(
        routes=[Gateway(handler=route_one)],
    ) as client:
        router = Router(
            path="/aditional/include",
            routes=[Include(routes=[Gateway("/second", handler=route_two)])],
        )
        client.app.add_router(router=router)

        response = client.get("/aditional/include/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT


def test_add_router_with_nested_includes(test_client_factory) -> None:
    """
    Adds a route to the router with nested includes.
    """

    with create_client(
        routes=[Gateway(handler=route_one)],
    ) as client:
        router = Router(
            path="/aditional/include",
            routes=[
                Include(
                    routes=[
                        Include(
                            routes=[
                                Include(
                                    routes=[
                                        Include(
                                            routes=[
                                                Include(
                                                    routes=[
                                                        Include(
                                                            routes=[
                                                                Include(
                                                                    routes=[
                                                                        Include(
                                                                            routes=[
                                                                                Gateway(
                                                                                    "/second",
                                                                                    handler=route_two,
                                                                                )
                                                                            ]
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ],
        )
        client.app.add_router(router=router)

        response = client.get("/aditional/include/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT


def test_add_router_with_nested_includes_mid_path(test_client_factory) -> None:
    """
    Adds a route to the router with nested includes.
    """

    with create_client(
        routes=[Gateway(handler=route_one)],
    ) as client:
        router = Router(
            path="/aditional/include",
            routes=[
                Include(
                    routes=[
                        Include(
                            routes=[
                                Include(
                                    routes=[
                                        Include(
                                            path="/test",
                                            routes=[
                                                Include(
                                                    routes=[
                                                        Include(
                                                            routes=[
                                                                Include(
                                                                    routes=[
                                                                        Include(
                                                                            routes=[
                                                                                Gateway(
                                                                                    "/second",
                                                                                    handler=route_two,
                                                                                )
                                                                            ]
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ],
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ],
        )

        client.app.add_router(router=router)

        response = client.get("/aditional/include/test/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT


def test_add_child_esmerald(test_client_factory):
    child = ChildEsmerald(routes=[Gateway(handler=route_one)])

    with create_client(routes=[]) as client:
        client.app.add_child_esmerald(path="/child", child=child)

        response = client.get("/child")

        assert response.status_code == 202
        assert response.json() == {"test": 1}


def test_add_child_esmerald_raise_error(test_client_factory):
    child = object()

    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[]) as client:
            client.app.add_child_esmerald(path="/child", child=child)


def test_add_include(test_client_factory):
    include = Include(path="/child", routes=[Gateway(handler=route_one)])

    with create_client(routes=[]) as client:
        client.app.add_include(include)

        response = client.get("/child")

        assert response.status_code == 202
        assert response.json() == {"test": 1}


def test_add_include_call_activate_openapi(test_client_factory):
    include = Include(path="/child", routes=[Gateway(handler=route_one)])

    with create_client(routes=[]) as client:
        with mock.patch("esmerald.applications.Esmerald.activate_openapi") as mock_call:
            client.app.add_include(include)

            response = client.get("/child")

            assert response.status_code == 202
            assert response.json() == {"test": 1}

            mock_call.assert_called_once()
