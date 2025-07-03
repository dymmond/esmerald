from typing import Any

import pytest

from esmerald import Context, Gateway, Request, get
from esmerald.testclient import create_client

pytestmark = pytest.mark.anyio


@get()
async def get_data(context: Context) -> dict[str, Any]:
    data = {
        "method": context.handler.methods,
        "middlewares": context.handler.middleware,
    }
    return data


def test_context(test_client_factory):
    with create_client(routes=[Gateway(path="/", handler=get_data)]) as client:
        response = client.get("/")

        assert response.json() == {"method": ["GET"], "middlewares": []}


@get()
async def get_context_route(context: Context) -> dict[str, Any]:
    data = {
        "method": context.handler.methods,
        "middlewares": context.handler.middleware,
    }
    return data


def test_context_route(test_client_factory):
    with create_client(routes=[Gateway(path="/", handler=get_context_route)]) as client:
        response = client.get("/")

        assert "method" in response.json()
        assert "middlewares" in response.json()


@get()
async def change_context(context: Context) -> dict[str, Any]:
    ctx = context
    ctx.add_to_context("call", "ok")
    return ctx.get_context_data()


def test_add_to_context(test_client_factory):
    with create_client(routes=[Gateway(path="/", handler=change_context)]) as client:
        response = client.get("/")

        assert response.json()["call"] == "ok"


@get()
async def context_with_request(
    context: Context,
    request: Request,
) -> Any:
    data = {
        "is_request": isinstance(request, Request),
        "is_context": isinstance(context, Context),
    }
    return data


def test_context_and_request(test_client_factory):
    with create_client(routes=[Gateway(path="/", handler=context_with_request)]) as client:
        response = client.get("/")

        assert response.json()["is_request"] is True
        assert response.json()["is_context"] is True


@get()
async def request_with_context(
    request: Request,
    context: Context,
) -> Any:
    data = {
        "is_request": isinstance(request, Request),
        "is_context": isinstance(context, Context),
    }
    return data


def test_request_and_context(test_client_factory):
    with create_client(routes=[Gateway(path="/", handler=request_with_context)]) as client:
        response = client.get("/")

        assert response.json()["is_request"] is True
        assert response.json()["is_context"] is True
