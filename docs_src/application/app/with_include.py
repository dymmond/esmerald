from esmerald.applications import Esmerald
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing.handlers import get, websocket
from esmerald.routing.router import Gateway, Include, WebSocketGateway
from esmerald.websockets import Websocket


@get()
async def homepage(request: Request) -> Response:
    return Response("Hello, world!")


@get()
async def me(request: Request) -> Response:
    username = "John Doe"
    return Response("Hello, %s!" % username)


@get()
def user(request: Request) -> Response:
    username = request.path_params["username"]
    return Response("Hello, %s!" % username)


@websocket()
async def websocket_endpoint(socket: Websocket) -> None:
    await websocket.accept()
    await websocket.send_text("Hello, websocket!")
    await websocket.close()


def startup():
    print("Up up we go!")


routes = [
    Include(
        routes=[
            Gateway(handler=homepage),
            Gateway(handler=me),
            Gateway(handler=user),
            WebSocketGateway(handler=websocket_endpoint),
        ]
    )
]

app = Esmerald(routes=routes, on_startup=[startup])
