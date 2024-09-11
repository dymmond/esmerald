from typing import Dict

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, get
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TestSettings


class PydanticError(BaseModel):
    detail: str
    code: int


@get(
    "/bar",
    tags=["bar"],
    responses={200: OpenAPIResponse(model=PydanticError, description="Pydantic response")},
)
async def bar(name: str) -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_module=TestSettings,
    contact={"name": "esmerald", "email": "esmerald@esmeral.dev"},
)


client = EsmeraldTestClient(app)


def test_openapi_query_params(test_client_factory):
    response = client.get("/openapi.json")

    assert response.status_code == 200, response.text

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Esmerald",
            "summary": "Esmerald application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "esmerald", "email": "esmerald@esmeral.dev"},
            "version": client.app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "tags": ["test", "bar"],
                    "summary": "Bar",
                    "description": "",
                    "operationId": "bar_bar_get",
                    "parameters": [
                        {
                            "name": "name",
                            "in": "query",
                            "required": True,
                            "deprecated": False,
                            "allowEmptyValue": False,
                            "allowReserved": False,
                            "schema": {"type": "string", "title": "Name"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pydantic response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
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
                "PydanticError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "PydanticError",
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
        "tags": ["test"],
    }
