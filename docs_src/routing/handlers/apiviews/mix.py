from pydantic import BaseModel

from esmerald import APIView, Esmerald, WebSocket, get, websocket
from esmerald.routing.gateways import Gateway


class Item(BaseModel):
    name: str
    sku: str


class MyAPIView(APIView):
    path = "/"

    @get(path="/")
    def get_person(self) -> Item: ...

    @websocket(path="/socket")
    async def ws(self, socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_json({"data": "123"})
        await socket.close()


app = Esmerald(routes=[Gateway(handler=MyAPIView)])
