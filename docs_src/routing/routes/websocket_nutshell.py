from ravyn import Ravyn, Websocket, WebSocketGateway, websocket


@websocket(path="/{path_param:str}")
async def world_socket(socket: Websocket) -> None:
    await socket.accept()
    msg = await socket.receive_json()
    assert msg
    assert socket
    await socket.close()


app = Ravyn(
    routes=[
        WebSocketGateway(handler=world_socket),
    ]
)
