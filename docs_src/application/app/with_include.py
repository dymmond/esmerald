from ravyn.applications import Ravyn
from ravyn.requests import Request
from ravyn.responses import Response
from ravyn.routing.handlers import get, websocket
from ravyn.routing.router import Gateway, Include, WebSocketGateway
from ravyn.websockets import Websocket


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
    await socket.accept()
    await socket.send_text("Hello, websocket!")
    await socket.close()


def startup():
    print("Up up we go!")


routes = [
    Include(
        routes=[
            Gateway("/home", handler=homepage),
            Gateway("/me", handler=me),
            Gateway("/user/{username}", handler=user),
            WebSocketGateway("/ws", handler=websocket_endpoint),
        ]
    )
]

app = Ravyn(routes=routes, on_startup=[startup])
