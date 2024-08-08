from typing import Optional

from esmerald import Esmerald, Gateway, get
from esmerald.testclient import EsmeraldTestClient


@get()
async def home(id: Optional[str]) -> None:
    """"""


app = Esmerald(
    routes=[
        Gateway("/home", handler=home),
        Gateway("/home/{id}", handler=home),
    ],
    enable_openapi=True,
)
client = EsmeraldTestClient(app)


def test_openapi_schema_operation_ids_when_same_handler_is_used(test_client_factory):
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
            "/home": {
                "get": {
                    "summary": "Home",
                    "operationId": "home_home_get",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": False,
                            "deprecated": False,
                            "allowEmptyValue": False,
                            "allowReserved": False,
                            "schema": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "title": "Id",
                            },
                        }
                    ],
                    "responses": {
                        "200": {"description": "Successful response"},
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
            },
            "/home/{id}": {
                "get": {
                    "summary": "Home",
                    "operationId": "home_home__id__get",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": False,
                            "deprecated": False,
                            "allowEmptyValue": False,
                            "allowReserved": False,
                            "schema": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "title": "Id",
                            },
                        }
                    ],
                    "responses": {
                        "200": {"description": "Successful response"},
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
            },
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
            }
        },
    }
