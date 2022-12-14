import pytest
from starlette import status

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.handlers import get, websocket
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


def test_add_route_from_router() -> None:
    """
    Adds a route to the router.
    """

    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        client.app.router.add_route("/second", handler=route_two)

        response = client.get("/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT


def test_add_route_from_application() -> None:
    """
    Adds a route to the application router.
    """

    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        client.app.add_route("/second", handler=route_two)

        response = client.get("/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        client.app.add_route("/third", handler=route_three)

        response = client.get("/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_raise_exception_on_add_route() -> None:
    """
    Raises improperly configured.
    """

    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[Gateway(handler=route_one)]) as client:
            handler = Gateway(handler=route_one)
            client.app.add_route("/one", handler=handler)


def test_websocket_handler_gateway_from_router() -> None:
    client = create_client(routes=[WebSocketGateway(path="/", handler=simple_websocket_handler)])

    with client.websocket_connect("/") as websocket_client:
        websocket_client.send_json({"data": "esmerald"})
        data = websocket_client.receive_json()
        assert data

    client.app.router.add_websocket_route("/ws", handler=simple_websocket_handler_two)
    with client.websocket_connect("/ws/websocket") as websocket_client:
        websocket_client.send_json({"data": "esmerald"})
        data = websocket_client.receive_json()
        assert data


def test_websocket_handler_gateway_from_application() -> None:
    client = create_client(routes=[WebSocketGateway(path="/", handler=simple_websocket_handler)])

    with client.websocket_connect("/") as websocket_client:
        websocket_client.send_json({"data": "esmerald"})
        data = websocket_client.receive_json()
        assert data

    client.app.add_websocket_route("/ws", handler=simple_websocket_handler_two)
    with client.websocket_connect("/ws/websocket") as websocket_client:
        websocket_client.send_json({"data": "esmerald"})
        data = websocket_client.receive_json()
        assert data


def test_raise_exception_on_add_websocket_route() -> None:
    """
    Raises improperly configured for websockets.
    """

    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[]) as client:
            handler = WebSocketGateway(handler=simple_websocket_handler)
            client.app.add_websocket_route("/ws", handler=handler)
