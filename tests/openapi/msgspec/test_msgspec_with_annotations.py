import msgspec
from typing_extensions import Annotated

from esmerald.datastructures.msgspec import Struct
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post
from esmerald.testclient import create_client
from tests.settings import TestSettings

Id = Annotated[int, msgspec.Meta(gt=0)]
Email = Annotated[str, msgspec.Meta(min_length=5, max_length=100, pattern="[^@]+@[^@]+\\.[^@]+")]


class Comment(Struct):
    id: Id
    email: Email


@post()
def user(payload: Comment) -> Comment:
    return payload


def test_user_msgspec_openapi(test_client_factory):
    with create_client(routes=[Gateway(handler=user)], settings_module=TestSettings) as client:
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
                "/": {
                    "post": {
                        "summary": "User",
                        "operationId": "user__post",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Comment"}
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "201": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            },
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/HTTPValidationError"
                                        }
                                    }
                                },
                            },
                        },
                        "deprecated": False,
                    }
                }
            },
            "components": {
                "schemas": {
                    "Comment": {
                        "properties": {
                            "id": {"type": "integer", "title": "Id"},
                            "email": {"type": "string", "title": "Email"},
                        },
                        "type": "object",
                        "required": ["id", "email"],
                        "title": "Comment",
                    },
                    "HTTPValidationError": {
                        "properties": {
                            "detail": {
                                "items": {"$ref": "#/components/schemas/ValidationError"},
                                "type": "array",
                                "title": "Detail",
                            }
                        },
                        "type": "object",
                        "title": "HTTPValidationError",
                    },
                    "ValidationError": {
                        "properties": {
                            "loc": {
                                "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                                "type": "array",
                                "title": "Location",
                            },
                            "msg": {"type": "string", "title": "Message"},
                            "type": {"type": "string", "title": "Error Type"},
                        },
                        "type": "object",
                        "required": ["loc", "msg", "type"],
                        "title": "ValidationError",
                    },
                }
            },
        }
