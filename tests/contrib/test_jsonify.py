from typing import Any

import pytest

from ravyn import Gateway, Ravyn, get
from ravyn.contrib.responses.json import jsonify
from ravyn.testclient import RavynTestClient


def test_jsonify_with_kwargs(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", status="ok")

    app = Ravyn(routes=[Gateway("/json", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/json")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello", "status": "ok"}
    assert response.headers["content-type"].startswith("application/json")


def test_jsonify_with_single_arg_list(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify([1, 2, 3])

    app = Ravyn(routes=[Gateway("/list", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/list")
    assert response.status_code == 200
    assert response.json() == [1, 2, 3]


def test_jsonify_with_multiple_args(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(1, 2, 3)

    app = Ravyn(routes=[Gateway("/multi", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/multi")
    assert response.status_code == 200
    assert response.json() == [1, 2, 3]


def test_jsonify_with_custom_status_code(test_client_factory):
    @get(status_code=201)
    async def endpoint() -> Any:
        return jsonify(message="created")

    app = Ravyn(routes=[Gateway("/created", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/created")
    assert response.status_code == 201
    assert response.json() == {"message": "created"}


def test_jsonify_with_headers(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", headers={"X-Custom": "value"})

    app = Ravyn(routes=[Gateway("/headers", handler=endpoint)])
    client = RavynTestClient(app)

    response = client.get("/headers")
    assert response.status_code == 200
    assert response.headers["x-custom"] == "value"
    assert response.json() == {"message": "Hello"}


def test_jsonify_with_cookies(test_client_factory):
    @get()
    async def endpoint() -> Any:
        return jsonify(message="Hello", cookies={"session": "abc123"})

    app = Ravyn(routes=[Gateway("/cookies", handler=endpoint)])
    client = RavynTestClient(app)

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

    app = Ravyn(routes=[Gateway("/error", handler=endpoint)])
    client = RavynTestClient(app)

    # since exception is raised inside endpoint, Ravyn will return 500
    response = client.get("/error")
    assert response.status_code == 500
