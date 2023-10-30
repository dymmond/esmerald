from typing import Any, Dict

from esmerald import Context, Gateway, get, route
from esmerald.testclient import create_client


@get()
async def get_data(context: Context) -> Dict[str, Any]:
    data = {
        "method": context.handler.http_methods,
        "middlewares": context.handler.middleware,
    }
    return data


def test_context(test_client_factory):
    with create_client(routes=[Gateway(handler=get_data)]) as client:
        response = client.get("/")

        assert response.json() == {"method": ["GET"], "middlewares": []}


@route(methods=["GET", "PUT", "POST"])
async def get_context_route(context: Context) -> Dict[str, Any]:
    data = {
        "method": context.handler.http_methods,
        "middlewares": context.handler.middleware,
    }
    return data


def test_context_route(test_client_factory):
    with create_client(routes=[Gateway(handler=get_context_route)]) as client:
        response = client.get("/")

        assert "method" in response.json()
        assert "middlewares" in response.json()


@get()
async def change_context(context: Context) -> Dict[str, Any]:
    ctx = context
    ctx.add_to_context("call", "ok")
    return ctx.get_context_data()


def test_add_to_context(test_client_factory):
    with create_client(routes=[Gateway(handler=change_context)]) as client:
        response = client.get("/")

        assert response.json()["call"] == "ok"
