from typing import Any

import pytest

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.handlers import websocket
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket


def test_websocket_handler_function_validation() -> None:
    def fn_without_socket_arg(websocket: WebSocket) -> None:
        ...  # pragma: no cover

    with pytest.raises(ImproperlyConfigured):
        websocket(path="/")(fn_without_socket_arg)  # type: ignore

    def fn_with_return_annotation(socket: WebSocket) -> dict:
        return {}  # pragma: no cover

    with pytest.raises(ImproperlyConfigured):
        websocket(path="/")(fn_with_return_annotation)  # type: ignore

    websocket_handler_with_no_fn = websocket(path="/")

    with pytest.raises(AttributeError):
        create_client(routes=[WebSocketGateway(path="/", handler=websocket_handler_with_no_fn)])

    with pytest.raises(ImproperlyConfigured):

        @websocket(path="/")
        async def websocket_handler_with_data_kwarg(socket: WebSocket, data: Any) -> None:
            ...  # pragma: no cover

    with pytest.raises(ImproperlyConfigured):

        @websocket(path="/")
        async def websocket_handler_with_request_kwarg(socket: WebSocket, request: Any) -> None:
            ...  # pragma: no cover

    with pytest.raises(ImproperlyConfigured):

        @websocket(path="/")  # type: ignore
        def sync_websocket_handler(socket: WebSocket, request: Any) -> None:
            ...  # pragma: no cover
