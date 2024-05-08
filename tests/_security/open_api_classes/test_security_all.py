from typing import Dict, List, Union

from pydantic import BaseModel

from esmerald import APIView, Gateway, JSONResponse, get
from esmerald.openapi.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery
from esmerald.openapi.security.http import Basic, Bearer, Digest
from esmerald.testclient import create_client
from tests.settings import TestSettings


class Error(BaseModel):
    status: int
    detail: str


class CustomResponse(BaseModel):
    status: str
    title: str
    errors: List[Error]


class JsonResponse(JSONResponse):
    media_type: str = "application/vnd.api+json"


class Item(BaseModel):
    sku: Union[int, str]


def test_security_api_key_in_cookie():
    class TestAPI(APIView):
        security = [
            Basic,
            Basic(),
            Bearer,
            Bearer(),
            Digest,
            Digest(),
            APIKeyInHeader,
            APIKeyInHeader(),
            APIKeyInHeader(name="X_TOKEN_HEADER"),
            APIKeyInQuery,
            APIKeyInQuery(),
            APIKeyInQuery(name="X_TOKEN_QUERY"),
            APIKeyInCookie,
            APIKeyInCookie(),
            APIKeyInCookie(name="X_TOKEN_COOKIE"),
        ]

        @get("/{pk:int}", response_class=JsonResponse)
        def read_people(self, pk: int) -> Dict[str, str]:
            """ """

    with create_client(
        routes=[Gateway(handler=TestAPI)],
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
                "/{pk}": {
                    "get": {
                        "summary": "Read People",
                        "operationId": "testapi_read_people__pk__get",
                        "deprecated": False,
                        "security": [
                            {
                                "Basic": {
                                    "type": "http",
                                    "name": "Basic",
                                    "in": "header",
                                    "scheme": "basic",
                                    "scheme_name": "Basic",
                                }
                            },
                            {
                                "Basic": {
                                    "type": "http",
                                    "name": "Basic",
                                    "in": "header",
                                    "scheme": "basic",
                                    "scheme_name": "Basic",
                                }
                            },
                            {
                                "Bearer": {
                                    "type": "http",
                                    "name": "Authorization",
                                    "in": "header",
                                    "scheme": "bearer",
                                    "scheme_name": "Bearer",
                                }
                            },
                            {
                                "Bearer": {
                                    "type": "http",
                                    "name": "Authorization",
                                    "in": "header",
                                    "scheme": "bearer",
                                    "scheme_name": "Bearer",
                                }
                            },
                            {
                                "Digest": {
                                    "type": "http",
                                    "name": "Authorization",
                                    "in": "header",
                                    "scheme": "digest",
                                    "scheme_name": "Digest",
                                }
                            },
                            {
                                "Digest": {
                                    "type": "http",
                                    "name": "Authorization",
                                    "in": "header",
                                    "scheme": "digest",
                                    "scheme_name": "Digest",
                                }
                            },
                            {
                                "APIKeyInHeader": {
                                    "type": "apiKey",
                                    "in": "header",
                                    "scheme_name": "APIKeyInHeader",
                                }
                            },
                            {
                                "APIKeyInHeader": {
                                    "type": "apiKey",
                                    "in": "header",
                                    "scheme_name": "APIKeyInHeader",
                                }
                            },
                            {
                                "APIKeyInHeader": {
                                    "type": "apiKey",
                                    "name": "X_TOKEN_HEADER",
                                    "in": "header",
                                    "scheme_name": "APIKeyInHeader",
                                }
                            },
                            {
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
                                }
                            },
                            {
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
                                }
                            },
                            {
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "name": "X_TOKEN_QUERY",
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
                                }
                            },
                            {
                                "APIKeyInCookie": {
                                    "type": "apiKey",
                                    "in": "cookie",
                                    "scheme_name": "APIKeyInCookie",
                                }
                            },
                            {
                                "APIKeyInCookie": {
                                    "type": "apiKey",
                                    "in": "cookie",
                                    "scheme_name": "APIKeyInCookie",
                                }
                            },
                            {
                                "APIKeyInCookie": {
                                    "type": "apiKey",
                                    "name": "X_TOKEN_COOKIE",
                                    "in": "cookie",
                                    "scheme_name": "APIKeyInCookie",
                                }
                            },
                        ],
                        "parameters": [
                            {
                                "name": "pk",
                                "in": "path",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {"type": "integer", "title": "Pk"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/vnd.api+json": {"schema": {"type": "string"}}
                                },
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
                    "Basic": {"type": "http", "name": "Basic", "in": "header", "scheme": "basic"},
                    "Bearer": {
                        "type": "http",
                        "name": "Authorization",
                        "in": "header",
                        "scheme": "bearer",
                    },
                    "Digest": {
                        "type": "http",
                        "name": "Authorization",
                        "in": "header",
                        "scheme": "digest",
                    },
                    "APIKeyInHeader": {"type": "apiKey", "name": "X_TOKEN_HEADER", "in": "header"},
                    "APIKeyInQuery": {"type": "apiKey", "name": "X_TOKEN_QUERY", "in": "query"},
                    "APIKeyInCookie": {"type": "apiKey", "name": "X_TOKEN_COOKIE", "in": "cookie"},
                },
            },
        }
