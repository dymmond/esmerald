from typing import Any

import pytest
from lilya.datastructures import Header
from typing_extensions import Literal

from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.handlers import websocket
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket


@pytest.mark.parametrize("mode", ["text", "binary"])
def test_websocket_send_receive_json(mode: "Literal['text', 'binary']") -> None:
    @websocket(path="/")
    async def websocket_handler(socket: WebSocket) -> None:
        await socket.accept()
        recv = await socket.receive_json(mode=mode)
        await socket.send_json({"message": recv}, mode=mode)
        await socket.close()

    with create_client(
        routes=[WebSocketGateway(path="/", handler=websocket_handler)]
    ).websocket_connect("/") as ws:
        ws.send_json({"hello": "world"}, mode=mode)
        data = ws.receive_json(mode=mode)
        assert data == {"message": {"hello": "world"}}


@pytest.mark.parametrize(
    "headers",
    [
        [(b"test", b"hello-world")],
        {"test": "hello-world"},
        Header({"test": "hello-world"}),
    ],
)
def test_accept_set_headers(headers: Any) -> None:
    @websocket("/")
    async def handler(socket: WebSocket) -> None:
        await socket.accept(headers=headers)
        await socket.close()

    with create_client(routes=[WebSocketGateway(path="/", handler=handler)]).websocket_connect(
        "/"
    ) as ws:
        ws.receive()
