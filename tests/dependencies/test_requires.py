from typing import Any

import anyio
import pytest

from esmerald import Gateway, Inject, Injects, JSONResponse, Requires, get
from esmerald.testclient import create_client
from esmerald.utils.dependencies import async_resolve_dependencies, resolve_dependencies


def get_user():
    return {"id": 1, "name": "Alice"}


def get_current_user(user: Any = Requires(get_user)):
    return user


async def get_async_user():
    await anyio.sleep(0.1)
    return {"id": 2, "name": "Bob"}


async def async_endpoint(current_user: Any = Requires(get_async_user)):
    return {"message": "Hello", "user": current_user}


def endpoint(current_user: Any = Requires(get_current_user)):
    return {"message": "Hello", "user": current_user}


@pytest.mark.asyncio
async def test_required_dependency_async():
    async_result = await async_resolve_dependencies(async_endpoint)

    assert async_result == {"message": "Hello", "user": {"id": 2, "name": "Bob"}}


def test_required_dependency():
    result = resolve_dependencies(endpoint)
    assert result == {"message": "Hello", "user": {"id": 1, "name": "Alice"}}


@get("/requires", dependencies={"current_user": Inject(get_current_user)})
async def get_requires(current_user: Any = Injects()) -> JSONResponse:
    return JSONResponse({"message": "Hello", "user": current_user})


def test_use_requires_in_function_dependencies_using_inject(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=get_requires),
        ],
    ) as client:
        response = client.get("/requires")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello", "user": {"id": 1, "name": "Alice"}}


@get("/requires-simple")
async def get_requires_simple(current_user: Any = Requires(endpoint)) -> JSONResponse:
    return JSONResponse(current_user)


def test_use_requires_as_a_non_dependency(test_app_client_factory):
    with create_client(
        routes=[
            Gateway(handler=get_requires_simple),
        ],
    ) as client:
        response = client.get("/requires-simple")

        assert response.status_code == 200
        assert response.json() == {"message": "Hello", "user": {"id": 1, "name": "Alice"}}


@get("/requires-typed-error")
async def get_requires_typed_error(current_user: int = Requires(endpoint)) -> JSONResponse: ...


def test_use_requires_raise_error_for_typing(test_app_client_factory):
    with create_client(
        routes=[
            Gateway(handler=get_requires_typed_error),
        ],
    ) as client:
        response = client.get("/requires-typed-error")

        assert response.status_code == 400


def test_openapi(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=get_requires_simple),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/openapi.json")

        assert response.status_code == 200
        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Esmerald",
                "summary": "Esmerald application",
                "description": "Highly scalable, performant, easy to learn and for every application.",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": client.app.version,
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/requires-simple": {
                    "get": {
                        "summary": "Get Requires Simple",
                        "description": "",
                        "operationId": "get_requires_simple_requires_simple_get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
        }
