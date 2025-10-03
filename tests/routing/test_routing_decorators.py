import typing

import pytest

from ravyn import Ravyn, Response, Router, WebSocket
from ravyn.testclient import TestClient

app = Ravyn()


@app.get("/")
async def homepage() -> Response:
    return Response("Hello, world", media_type="text/plain")


@app.get("/users")
async def users() -> Response:
    return Response("All users", media_type="text/plain")


@app.post("/users")
def create_users() -> Response:
    return Response("User created", media_type="text/plain")


@app.route("/generic", methods=["DELETE", "POST"])
async def generic() -> Response:
    return Response("Generic route", media_type="text/plain")


@app.route("/params/{name}/<age:int>", methods=["GET", "POST"])
async def params(name: str, age: int) -> Response:
    return Response(f"Name {name} with age {age}", media_type="text/plain")


@app.websocket(path="/ws")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


@pytest.fixture
def another_client(test_client_factory: typing.Callable[..., TestClient]):
    with test_client_factory(app) as client:
        yield client


def test_decorators(another_client: TestClient):
    response = another_client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, world"

    response = another_client.get("/users")
    assert response.status_code == 200
    assert response.text == "All users"

    response = another_client.post("/users")
    assert response.status_code == 200
    assert response.text == "User created"

    response = another_client.post("/generic")
    assert response.status_code == 200
    assert response.text == "Generic route"

    response = another_client.delete("/generic")
    assert response.status_code == 200
    assert response.text == "Generic route"

    response = another_client.get("/generic")
    assert response.status_code == 405

    response = another_client.get("/params/John/20")
    assert response.status_code == 200
    assert response.text == "Name John with age 20"

    response = another_client.post("/params/John/20")
    assert response.status_code == 200
    assert response.text == "Name John with age 20"

    with another_client.websocket_connect("/ws") as session:
        text = session.receive_text()
        assert text == "Hello, world!"


router = Router()


@router.get("/another")
async def another_homepage() -> Response:
    return Response("Hello, world", media_type="text/plain")


@router.get("/another/users")
async def another_users() -> Response:
    return Response("All users", media_type="text/plain")


@router.post("/another/users")
def another_create_users() -> Response:
    return Response("User created", media_type="text/plain")


@router.route("/another/generic", methods=["DELETE", "POST"])
async def another_generic() -> Response:
    return Response("Generic route", media_type="text/plain")


@router.route("/another/params/{name}/<age:int>", methods=["GET", "POST"])
async def another_params(name: str, age: int) -> Response:
    return Response(f"Name {name} with age {age}", media_type="text/plain")


@router.websocket(path="/another/ws")
async def another_websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


another_app = Ravyn()
another_app.add_router(router)


@pytest.fixture
def client(test_client_factory: typing.Callable[..., TestClient]):
    with test_client_factory(another_app) as client:
        yield client


def test_router_decorators(client: TestClient):
    response = client.get("/another")
    assert response.status_code == 200
    assert response.text == "Hello, world"

    response = client.get("/another/users")
    assert response.status_code == 200
    assert response.text == "All users"

    response = client.post("/another/users")
    assert response.status_code == 200
    assert response.text == "User created"

    response = client.post("/another/generic")
    assert response.status_code == 200
    assert response.text == "Generic route"

    response = client.delete("/another/generic")
    assert response.status_code == 200
    assert response.text == "Generic route"

    response = client.get("/another/generic")
    assert response.status_code == 405

    response = client.get("/another/params/John/20")
    assert response.status_code == 200
    assert response.text == "Name John with age 20"

    response = client.post("/another/params/John/20")
    assert response.status_code == 200
    assert response.text == "Name John with age 20"

    with client.websocket_connect("/another/ws") as session:
        text = session.receive_text()
        assert text == "Hello, world!"
