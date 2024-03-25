import pytest
from lilya import status

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.handlers import delete, get, post, put, route, websocket
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


@route(status_code=status.HTTP_202_ACCEPTED, methods=["GET", "POST", "PUT"])
def routes_multiple() -> dict:
    return {"test": 1}


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


def test_add_route_from_router(test_client_factory) -> None:
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


def test_add_route_from_router_multiple_methods(test_client_factory) -> None:
    """
    Adds a route to the router using @route
    """

    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        client.app.router.add_route("/multiple", handler=routes_multiple)

        response = client.get("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.post("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.put("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED


def test_add_route_from_application(test_client_factory) -> None:
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


def test_add_route_multiple_from_application(test_client_factory) -> None:
    """
    Adds a route to the application router using @route
    """

    with create_client(routes=[Gateway(handler=route_one)]) as client:
        response = client.get("/")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        client.app.router.add_route("/multiple", handler=routes_multiple)

        response = client.get("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.post("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.put("/multiple")

        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED


def test_raise_exception_on_add_route(test_client_factory) -> None:
    """
    Raises improperly configured.
    """

    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[Gateway(handler=route_one)]) as client:
            handler = Gateway(handler=route_one)
            client.app.add_route("/one", handler=handler)


def test_websocket_handler_gateway_from_router(test_client_factory) -> None:
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


def test_websocket_handler_gateway_from_application(test_client_factory) -> None:
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


def test_raise_exception_on_add_websocket_route(test_client_factory) -> None:
    """
    Raises improperly configured for websockets.
    """

    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[]) as client:
            handler = WebSocketGateway(handler=simple_websocket_handler)
            client.app.add_websocket_route("/ws", handler=handler)


@pytest.mark.parametrize(
    "method, fn_path, status_code, response_text",
    [
        (get, "/get", 200, "ok"),
        (post, "/post", 200, "ok"),
        (put, "/put", 200, "ok"),
        (delete, "/delete", 200, "ok"),
        (post, "/another-post", 201, "created!"),
        (put, "/another-post", 201, "updated!"),
        (delete, "/another-post", 201, "updated!"),
        (get, "/another-post", 201, "updated!"),
    ],
)
def test_add_apiview_multiple_from_application(
    method, fn_path, status_code, response_text, test_client_factory
) -> None:
    """
    Adds a route to the application router using @route
    """

    class View(APIView):
        path = "/"

        @method(fn_path, status_code=status_code)
        async def test(self) -> str:
            return response_text

    with create_client(routes=[]) as client:
        gateway = Gateway(handler=View)
        client.app.add_apiview(value=gateway)

        response = getattr(client, method.__name__)(fn_path)

        assert response.json() == response_text
        assert response.status_code == status_code
