from typing import Any

import pytest

from esmerald import Esmerald, Gateway, get
from esmerald.contrib.responses.json import jsonify
from esmerald.testclient import EsmeraldTestClient


def test_jsonify_with_kwargs(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", status="ok")

    app = Esmerald(routes=[Gateway("/json", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/json")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello", "status": "ok"}
    assert response.headers["content-type"].startswith("application/json")


def test_jsonify_with_single_arg_list(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify([1, 2, 3])

    app = Esmerald(routes=[Gateway("/list", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/list")
    assert response.status_code == 200
    assert response.json() == [1, 2, 3]


def test_jsonify_with_multiple_args(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(1, 2, 3)

    app = Esmerald(routes=[Gateway("/multi", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/multi")
    assert response.status_code == 200
    assert response.json() == [1, 2, 3]


def test_jsonify_with_custom_status_code(test_client_factory):
    @get(status_code=201)
    async def endpoint() -> Any:
        return jsonify(message="created")

    app = Esmerald(routes=[Gateway("/created", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/created")
    assert response.status_code == 201
    assert response.json() == {"message": "created"}


def test_jsonify_with_headers(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", headers={"X-Custom": "value"})

    app = Esmerald(routes=[Gateway("/headers", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/headers")
    assert response.status_code == 200
    assert response.headers["x-custom"] == "value"
    assert response.json() == {"message": "Hello"}


def test_jsonify_with_cookies(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", cookies={"session": "abc123"})

    app = Esmerald(routes=[Gateway("/cookies", handler=endpoint)])
    client = EsmeraldTestClient(app)

    response = client.get("/cookies")
    assert response.status_code == 200
    assert "set-cookie" in response.headers
    assert response.headers["set-cookie"].startswith("session=abc123")
    assert response.json() == {"message": "Hello"}


def test_jsonify_raises_on_args_and_kwargs(test_client_factory):
    @get()
    async def endpoint() -> Any:
        with pytest.raises(TypeError):
            return jsonify({"a": 1}, b=2)

    app = Esmerald(routes=[Gateway("/error", handler=endpoint)])
    client = EsmeraldTestClient(app)

    # since exception is raised inside endpoint, Esmerald will return 500
    response = client.get("/error")
    assert response.status_code == 500
