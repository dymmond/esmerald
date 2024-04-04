from typing import Dict, List, Union

import pytest
from pydantic import BaseModel

from esmerald import Gateway, JSONResponse, get
from esmerald.openapi.security.api_key import APIKeyInQuery
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


@pytest.mark.parametrize("auth", [APIKeyInQuery, APIKeyInQuery()])
def test_security_api_key_in_query(auth):
    @get(
        response_class=JsonResponse,
        security=[auth],
    )
    def read_people() -> Dict[str, str]:
        """ """

    with create_client(
        routes=[Gateway(handler=read_people)],
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
                "/": {
                    "get": {
                        "summary": "Read People",
                        "operationId": "read_people__get",
                        "deprecated": False,
                        "security": [
                            {
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/vnd.api+json": {"schema": {"type": "string"}}
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "securitySchemes": {"APIKeyInQuery": {"type": "apiKey", "in": "query"}}
            },
        }


@pytest.mark.parametrize(
    "token,value",
    [
        (APIKeyInQuery(name="Authorization"), "Authorization"),
        (APIKeyInQuery(name="X_TOKEN"), "X_TOKEN"),
        (APIKeyInQuery(name="test"), "test"),
    ],
    ids=["x-api-token", "x-token", "test"],
)
def test_security_api_key_in_query_value(token, value):
    @get(
        response_class=JsonResponse,
        security=[token],
    )
    def read_people() -> Dict[str, str]:
        """ """

    with create_client(
        routes=[Gateway(handler=read_people)],
        enable_openapi=True,
        include_in_schema=True,
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
                "/": {
                    "get": {
                        "summary": "Read People",
                        "operationId": "read_people__get",
                        "deprecated": False,
                        "security": [
                            {
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "name": value,
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/vnd.api+json": {"schema": {"type": "string"}}
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "APIKeyInQuery": {"type": "apiKey", "name": value, "in": "query"}
                }
            },
        }
