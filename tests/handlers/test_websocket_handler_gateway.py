from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.handlers import websocket
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket


def test_websocket_handler_gateway() -> None:
    @websocket(path="/")
    async def simple_websocket_handler(socket: WebSocket) -> None:
        await socket.accept()
        data = await socket.receive_json()

        assert data
        await socket.send_json({"data": "esmerald"})
        await socket.close()

    client = create_client(routes=[WebSocketGateway(path="/", handler=simple_websocket_handler)])

    with client.websocket_connect("/") as websocket_client:
        websocket_client.send_json({"data": "esmerald"})
        data = websocket_client.receive_json()
        assert data
