from esmerald import Esmerald, Websocket, WebSocketGateway, websocket


@websocket(path="/{path_param:str}")
async def world_socket(self, socket: Websocket) -> None:
    await socket.accept()
    msg = await socket.receive_json()
    assert msg
    assert socket
    await socket.close()


app = Esmerald(
    routes=[
        WebSocketGateway(handler=world_socket),
    ]
)
