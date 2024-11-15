from typing import Any, Optional

from esmerald import Gateway, Inject, Injects, get
from esmerald.security.oauth2 import OAuth2AuthorizationCodeBearer
from esmerald.testclient import create_client

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="authorize", tokenUrl="token", auto_error=True
)


@get("/items", dependencies={"token": Inject(oauth2_scheme)}, security=[oauth2_scheme])
async def read_items(token: Optional[str] = Injects()) -> dict[str, Any]:
    return {"token": token}


def test_no_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Non-existent testtoken"})
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200, response.text
        assert response.json() == {"token": "testtoken"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200, response.text

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
                "/items": {
                    "get": {
                        "summary": "Read Items",
                        "description": "",
                        "operationId": "read_items_items_get",
                        "deprecated": False,
                        "security": [
                            {
                                "OAuth2AuthorizationCodeBearer": {
                                    "type": "oauth2",
                                    "flows": {
                                        "authorizationCode": {
                                            "authorizationUrl": "authorize",
                                            "tokenUrl": "token",
                                            "scopes": {},
                                        }
                                    },
                                    "scheme_name": "OAuth2AuthorizationCodeBearer",
                                }
                            }
                        ],
                        "parameters": [
                            {
                                "name": "token",
                                "in": "query",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {
                                    "anyOf": [{"type": "string"}, {"type": "null"}],
                                    "title": "Token",
                                },
                            }
                        ],
                        "responses": {
                            "200": {
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
                    }
                }
            },
            "components": {
                "schemas": {
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
                },
                "securitySchemes": {
                    "OAuth2AuthorizationCodeBearer": {
                        "type": "oauth2",
                        "flows": {
                            "authorizationCode": {
                                "authorizationUrl": "authorize",
                                "tokenUrl": "token",
                                "scopes": {},
                            }
                        },
                    }
                },
            },
        }
