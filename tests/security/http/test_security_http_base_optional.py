from typing import Any, Optional

from esmerald import Gateway, Inject, Injects, get
from esmerald.security.http import HTTPAuthorizationCredentials, HTTPBase
from esmerald.testclient import create_client

security = HTTPBase(scheme="Other", auto_error=False)


@get(
    "/users/me",
    dependencies={"credentials": Inject(security)},
    security=[security],
)
def read_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Injects(),
) -> Any:
    if credentials is None:
        return {"msg": "Create an account first"}
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


def test_security_http_base():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me", headers={"Au thorization": "Other foobar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"scheme": "Other", "credentials": "foobar"}


def test_security_http_base_no_credentials():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_openapi_schema():
    with create_client(routes=[Gateway(handler=read_current_user)], enable_openapi=True) as client:
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
                                "HTTPBase": {
                                    "type": "http",
                                    "scheme": "Other",
                                    "scheme_name": "HTTPBase",
                                }
                            }
                        ],
                        "parameters": [
                            {
                                "name": "credentials",
                                "in": "query",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {
                                    "anyOf": [
                                        {
                                            "$ref": "#/components/schemas/HTTPAuthorizationCredentials"
                                        },
                                        {"type": "null"},
                                    ],
                                    "title": "Credentials",
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
                    "HTTPAuthorizationCredentials": {
                        "properties": {
                            "scheme": {"type": "string", "title": "Scheme"},
                            "credentials": {"type": "string", "title": "Credentials"},
                        },
                        "type": "object",
                        "required": ["scheme", "credentials"],
                        "title": "HTTPAuthorizationCredentials",
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
                },
                "securitySchemes": {"HTTPBase": {"type": "http", "scheme": "Other"}},
            },
        }
