from pydantic import BaseModel, EmailStr

from ravyn import (
    APIView,
    ChildRavyn,
    Ravyn,
    Gateway,
    Include,
    Request,
    WebSocket,
    WebSocketGateway,
    get,
    post,
    websocket,
)


@get("/me")
async def me(request: Request) -> str:
    return "Hello, world!"


@websocket(path="/ws")
async def websocket_endpoint_include(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, new world!")
    await socket.close()


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserApiView(APIView):
    path = "/users"

    @post("/create")
    async def create_user(self, data: User, request: Request) -> None: ...

    @websocket(path="/ws")
    async def websocket_endpoint(self, socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_text("Hello, world!")
        await socket.close()


child_esmerald = ChildRavyn(routes=[Gateway(handler=UserApiView)])

app = Ravyn(
    routes=[
        Include(
            "/",
            routes=[
                Gateway(handler=me),
                WebSocketGateway(handler=websocket_endpoint_include),
                Include("/child", child_esmerald),
            ],
        )
    ]
)
