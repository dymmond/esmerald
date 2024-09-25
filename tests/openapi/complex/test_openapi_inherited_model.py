from typing import Dict

from pydantic import BaseModel, EmailStr

from esmerald import Gateway, Include, get
from esmerald.testclient import create_client


class Base(BaseModel):
    email: EmailStr


class PydanticItem(Base):
    name: str


@get("/item", tags=["bar"])
async def item(pydantic: PydanticItem) -> Dict[str, str]:
    return {"pydantic": pydantic}


def test_inheritance(test_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[Gateway(handler=item)],
            )
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
                "/item": {
                    "get": {
                        "tags": ["bar"],
                        "summary": "Item",
                        "description": "",
                        "operationId": "item_item_get",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DataField"}
                                }
                            },
                            "required": True,
                        },
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
                        "deprecated": False,
                    }
                }
            },
            "components": {
                "schemas": {
                    "DataField": {
                        "properties": {"pydantic": {"$ref": "#/components/schemas/PydanticItem"}},
                        "type": "object",
                        "required": ["pydantic"],
                        "title": "DataField",
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
                    "PydanticItem": {
                        "properties": {
                            "email": {"type": "string", "format": "email", "title": "Email"},
                            "name": {"type": "string", "title": "Name"},
                        },
                        "type": "object",
                        "required": ["email", "name"],
                        "title": "PydanticItem",
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
