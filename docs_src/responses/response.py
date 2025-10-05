from ravyn import (
    APIView,
    Ravyn,
    Gateway,
    Request,
    Response,
    WebSocket,
    get,
    post,
    status,
    websocket,
)


class World(APIView):
    @get(path="/{url}")
    async def home(self, request: Request, url: str) -> Response:
        return Response(f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(self, request: Request, url: str) -> Response: ...

    @websocket(path="/{path_param:str}")
    async def pluto(self, socket: WebSocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()


app = Ravyn(routes=[Gateway("/world", handler=World)])
