from typing import Any, Optional

from pydantic import BaseModel

from esmerald import Gateway, Inject, Injects, Security, get
from esmerald.security.api_key import APIKeyInHeader
from esmerald.testclient import create_client

api_key = APIKeyInHeader(name="key", auto_error=False)


class User(BaseModel):
    username: str


def get_current_user(oauth_header: Optional[str] = Security(api_key)):
    if oauth_header is None:
        return None
    user = User(username=oauth_header)
    return user


@get("/users/me", security=[api_key], dependencies={"current_user": Inject(get_current_user)})
def read_current_user(current_user: Optional[User] = Injects()) -> Any:
    if current_user is None:
        return {"msg": "Create an account first"}
    else:
        return current_user


def test_security_api_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
    ) as client:
        response = client.get("/users/me", headers={"key": "secret"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "secret"}


def test_security_api_key_no_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
    ) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
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
                "/users/me": {
                    "get": {
                        "summary": "Read Current User",
                        "description": "",
                        "operationId": "read_current_user_users_me_get",
                        "deprecated": False,
                        "security": [
                            {
                                "APIKeyInHeader": {
                                    "type": "apiKey",
                                    "name": "key",
                                    "in": "header",
                                    "scheme_name": "APIKeyInHeader",
                                }
                            }
                        ],
                        "parameters": [
                            {
                                "name": "current_user",
                                "in": "query",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {
                                    "anyOf": [
                                        {"$ref": "#/components/schemas/User"},
                                        {"type": "null"},
                                    ],
                                    "title": "Current User",
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
                    "User": {
                        "properties": {"username": {"type": "string", "title": "Username"}},
                        "type": "object",
                        "required": ["username"],
                        "title": "User",
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
                    "APIKeyInHeader": {"type": "apiKey", "name": "key", "in": "header"}
                },
            },
        }
