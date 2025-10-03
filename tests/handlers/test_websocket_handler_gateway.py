from ravyn.routing.gateways import WebSocketGateway
from ravyn.routing.handlers import websocket
from ravyn.testclient import create_client
from ravyn.websockets import WebSocket


def test_websocket_handler_gateway() -> None:
    @websocket(path="/")
    async def simple_websocket_handler(socket: WebSocket) -> None:
        await socket.accept()
        data = await socket.receive_json()

        assert data
        await socket.send_json({"data": "ravyn"})
        await socket.close()

    client = create_client(routes=[WebSocketGateway(path="/", handler=simple_websocket_handler)])

    with client.websocket_connect("/") as websocket_client:
        websocket_client.send_json({"data": "ravyn"})
        data = websocket_client.receive_json()
        assert data
