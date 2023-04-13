from starlette import status

from esmerald import ChildEsmerald
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get, websocket
from esmerald.routing.router import Include, Router
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket


@get(status_code=status.HTTP_202_ACCEPTED)
def route_one() -> dict:
    return {"test": 1}


@get(status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_two() -> dict:
    return {"test": 2}


@get(status_code=status.HTTP_200_OK)
def route_three() -> dict:
    return {"test": 3}


@websocket(path="/")
async def simple_websocket_handler(socket: WebSocket) -> None:
    await socket.accept()
    data = await socket.receive_json()

    assert data
    await socket.send_json({"data": "esmerald"})
    await socket.close()


@websocket(path="/websocket")
async def simple_websocket_handler_two(socket: WebSocket) -> None:
    await socket.accept()
    data = await socket.receive_json()

    assert data
    await socket.send_json({"data": "esmerald"})
    await socket.close()


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
