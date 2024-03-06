import pytest

from esmerald import Gateway, Include, Request, WebSocket, WebSocketGateway, get, websocket
from esmerald.enums import MediaType
from esmerald.permissions import AllowAny, DenyAll
from esmerald.responses import JSONResponse
from esmerald.testclient import create_client
from lilya.responses import Response


@get(path="/", permissions=[DenyAll])
async def deny_access(request: Request) -> JSONResponse:
    return JSONResponse("Hello, world")


@get(path="/", permissions=[AllowAny])
async def allow_access(request: Request) -> JSONResponse:
    return JSONResponse("Hello, world")


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def homepage(request: Request) -> Response:
    return Response("Hello, world")


@websocket(path="/")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


routes = [
    Gateway("/", handler=homepage, name="homepage"),
    Include(
        "/nested",
        routes=[
            Include(
                path="/test/",
                routes=[Gateway(path="/", handler=homepage, name="nested")],
            ),
            Include(
                path="/another",
                routes=[
                    Include(
                        path="/test",
                        routes=[Gateway(path="/{param}", handler=homepage, name="nested")],
                    )
                ],
            ),
        ],
    ),
    Include(
        "/static",
        app=Response("xxxxx", media_type=MediaType.PNG, status_code=200),
    ),
    WebSocketGateway("/ws", handler=websocket_endpoint, name="websocket_endpoint"),
    Gateway("/deny", handler=deny_access, name="deny_access"),
    Gateway("/allow", handler=allow_access, name="allow_access"),
]


@pytest.mark.filterwarnings(
    r"ignore"
    r":Trying to detect encoding from a tiny portion of \(5\) byte\(s\)\."
    r":UserWarning"
    r":charset_normalizer.api"
)
def test_router():
    with create_client(routes=routes) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, world"

        response = client.post("/")
        assert response.status_code == 405
        assert response.json()["detail"] == "Method POST not allowed."
        assert response.headers["content-type"] == MediaType.JSON

        response = client.get("/foo")
        assert response.status_code == 404
        assert response.json()["detail"] == "The resource cannot be found."

        response = client.get("/static/123")
        assert response.status_code == 200
        assert response.text == "xxxxx"

        response = client.get("/nested/test")
        assert response.status_code == 200
        assert response.text == "Hello, world"

        response = client.get("/nested/another/test/fluid")
        assert response.status_code == 200
        assert response.text == "Hello, world"

        with client.websocket_connect("/ws") as session:
            text = session.receive_text()
            assert text == "Hello, world!"
