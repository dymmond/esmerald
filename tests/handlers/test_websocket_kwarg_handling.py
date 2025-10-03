from ravyn.params import Header
from ravyn.routing.gateways import WebSocketGateway
from ravyn.routing.handlers import websocket
from ravyn.testclient import create_client
from ravyn.websockets import WebSocket


def test_handle_websocket_params_parsing() -> None:
    @websocket(path="/{socket_id:int}")
    async def websocket_handler(
        socket: WebSocket,
        headers: dict,
        query: dict,
        cookies: dict,
        socket_id: int,
        qp: int,
        hp: str = Header(value="some-header"),
    ) -> None:
        assert socket_id
        assert headers
        assert query
        assert cookies
        assert qp

        assert hp
        await socket.accept()

        data = await socket.receive_json()

        assert data
        await socket.send_json({"data": "ravyn"})
        await socket.close()

    client = create_client(routes=[WebSocketGateway(path="/", handler=websocket_handler)])

    with client.websocket_connect(
        "/1?qp=1", headers={"some-header": "abc"}, cookies={"cookie": "yum"}
    ) as ws:
        ws.send_json({"data": "ravyn"})
        data = ws.receive_json()
        assert data
