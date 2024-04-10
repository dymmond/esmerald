from __future__ import annotations

from esmerald import APIView, Gateway, Include, post
from esmerald.testclient import create_client
from tests.settings import TestSettings


class UserAPIView(APIView):
    tags: list[str] = ["User"]

    @post(path="/")
    async def create(self) -> str: ...


class ProfileAPIView(APIView):
    tags: list[str] = ["Profile"]

    @post(path="/")
    async def create(self) -> str: ...


user_routes = [Gateway(handler=UserAPIView)]
profile_routes = [Gateway(handler=ProfileAPIView)]

route_patterns = [
    Include(
        "/admin",
        routes=[
            Include(
                "/users",
                namespace="tests.openapi.test_duplicate_operation_id",
                pattern="user_routes",
            ),
            Include(
                "/profiles",
                namespace="tests.openapi.test_duplicate_operation_id",
                pattern="profile_routes",
            ),
        ],
    )
]


def test_open_api_schema(test_client_factory):
    with create_client(
        routes=[Include(path="/api/v1", namespace="tests.openapi.test_duplicate_operation_id")],
        enable_openapi=True,
        include_in_schema=True,
        settings_module=TestSettings,
    ) as client:
        response = client.get("/openapi.json")

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
                "/api/v1/admin/users": {
                    "post": {
                        "tags": ["User"],
                        "summary": "Create",
                        "operationId": "userapiview_create__post",
                        "responses": {
                            "201": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
                "/api/v1/admin/profiles": {
                    "post": {
                        "tags": ["Profile"],
                        "summary": "Create",
                        "operationId": "profileapiview_create__post",
                        "responses": {
                            "201": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
            },
        }
