from esmerald import get, post
from esmerald.testclient import create_client
from esmerald.utils.decorators import controller


@controller(path="/items", tags=["controller", "decorator"])
class ItemHandler:

    @get("/{item_id}")
    async def get_item(self, item_id: int) -> dict:
        return {"item_id": item_id}

    @post("/")
    async def create_item(self, data: dict) -> dict:
        return {"message": "Item created", "data": data}


def test_controller_decorator(test_client_factory):
    with create_client(routes=[ItemHandler]) as client:

        response = client.get("/items/1")
        assert response.status_code == 200
        assert response.json() == {"item_id": 1}

        response = client.post("/items/", json={"name": "test"})
        assert response.status_code == 201
        assert response.json() == {"message": "Item created", "data": {"name": "test"}}


def test_openapi_schema(test_client_factory):
    with create_client(routes=[ItemHandler]) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200

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
                    "post": {
                        "tags": ["controller", "decorator"],
                        "summary": "Itemhandler",
                        "description": "",
                        "operationId": "itemhandler_items_post",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "additionalProperties": True,
                                        "type": "object",
                                        "title": "Body_itemhandler_items_post",
                                    }
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
                },
                "/items/{item_id}": {
                    "get": {
                        "tags": ["controller", "decorator"],
                        "summary": "Itemhandler",
                        "description": "",
                        "operationId": "itemhandler_items__item_id__get",
                        "parameters": [
                            {
                                "name": "item_id",
                                "in": "path",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {"type": "integer", "title": "Item Id"},
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
