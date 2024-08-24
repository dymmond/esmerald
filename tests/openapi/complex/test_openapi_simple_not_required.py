from typing import Dict, Union

from msgspec import Struct
from pydantic import BaseModel

from esmerald import Gateway, Include, get
from esmerald.testclient import create_client


class PydanticItem(BaseModel):
    name: str


class MsgSpecItem(Struct):
    name: str


@get("/item", tags=["bar"])
async def item(pydantic: PydanticItem, msgspec: Union[MsgSpecItem, None]) -> Dict[str, str]:
    return {"pydantic": pydantic, "msgspec": msgspec}


def test_complex_simple_not_required(test_client_factory):
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
                        "properties": {
                            "pydantic": {"$ref": "#/components/schemas/PydanticItem"},
                            "msgspec": {
                                "anyOf": [
                                    {"$ref": "#/components/schemas/MsgSpecItem"},
                                    {"type": "null"},
                                ]
                            },
                        },
                        "type": "object",
                        "required": ["pydantic", "msgspec"],
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
                    "MsgSpecItem": {
                        "properties": {"name": {"type": "string", "title": "Name"}},
                        "type": "object",
                        "required": ["name"],
                        "title": "MsgSpecItem",
                    },
                    "PydanticItem": {
                        "properties": {"name": {"type": "string", "title": "Name"}},
                        "type": "object",
                        "required": ["name"],
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
