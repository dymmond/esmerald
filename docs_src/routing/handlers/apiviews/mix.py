from pydantic import BaseModel

from ravyn import Controller, Ravyn, WebSocket, get, websocket
from ravyn.routing.gateways import Gateway


class Item(BaseModel):
    name: str
    sku: str


class MyAPIView(Controller):
    path = "/"

    @get(path="/")
    def get_person(self) -> Item: ...

    @websocket(path="/socket")
    async def ws(self, socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_json({"data": "123"})
        await socket.close()


app = Ravyn(routes=[Gateway(handler=MyAPIView)])
