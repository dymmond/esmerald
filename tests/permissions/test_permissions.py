from typing import TYPE_CHECKING

import pytest
from lilya.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from lilya.websockets import WebSocketDisconnect

from esmerald.applications import ChildEsmerald
from esmerald.permissions import AllowAny, BasePermission, DenyAll
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.handlers import get, route, websocket
from esmerald.routing.router import Include
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket

if TYPE_CHECKING:
    from esmerald.types import APIGateHandler  # pragma: no cover


class LocalPermission(BasePermission):
    def has_permission(self, request: "Request", apiview: "APIGateHandler"):
        if not request.headers.get("allow_all"):
            return False
        return True


class ApplicationPermission(BasePermission):
    def has_permission(self, request: "Request", apiview: "APIGateHandler"):
        if not request.headers.get("Authorization"):
            return False
        return True


def test_permissions_with_http_handler_one() -> None:
    @get(path="/secret", permissions=[LocalPermission])
    def my_http_route_handler() -> None: ...

    with create_client(
        permissions=[ApplicationPermission],
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/secret")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_http_handler_two() -> None:
    @route(methods=["GET"], path="/secret", permissions=[LocalPermission])
    async def my_asgi_handler() -> None: ...

    with create_client(
        permissions=[ApplicationPermission], routes=[Gateway(handler=my_asgi_handler)]
    ) as client:
        response = client.get("/secret")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_websocket_handler() -> None:
    @websocket(path="/", permissions=[LocalPermission])
    async def my_websocket_route_handler(socket: WebSocket) -> None:
        await socket.accept()
        data = await socket.receive_json()
        assert data
        await socket.send_json({"data": "123"})
        await socket.close()

    client = create_client(routes=WebSocketGateway(handler=my_websocket_route_handler))

    with pytest.raises(WebSocketDisconnect), client.websocket_connect("/") as ws:
        ws.send_json({"data": "123"})  # pragma: no cover

    with client.websocket_connect("/", headers={"allow_all": "true"}) as ws:
        ws.send_json({"data": "123"})


def test_permissions_with_child_esmerald() -> None:
    @route(methods=["GET"], path="/secret", permissions=[LocalPermission])
    async def my_asgi_handler() -> None: ...

    child = ChildEsmerald(routes=[Gateway(handler=my_asgi_handler)])

    with create_client(permissions=[ApplicationPermission], routes=[Include(app=child)]) as client:
        response = client.get("/secret")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_child_esmerald_two() -> None:
    @route(methods=["GET"], path="/secret", permissions=[ApplicationPermission])
    async def my_asgi_handler() -> None: ...

    child = ChildEsmerald(routes=[Gateway(handler=my_asgi_handler)])

    with create_client(permissions=[LocalPermission], routes=[Include(app=child)]) as client:
        response = client.get("/secret")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "allow_all"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_child_esmerald_three() -> None:
    @route(methods=["GET"], path="/secret")
    async def my_asgi_handler() -> None:
        """ """

    child = ChildEsmerald(routes=[Gateway(handler=my_asgi_handler)], permissions=[AllowAny])

    with create_client(permissions=[DenyAll], routes=[Include(app=child)]) as client:
        response = client.get("/secret")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
