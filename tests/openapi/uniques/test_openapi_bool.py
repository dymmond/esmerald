from esmerald import Gateway, JSONResponse, get
from esmerald.testclient import create_client


@get("/bool")
async def check_bool(a_value: bool) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param(test_client_factory):
    with create_client(routes=Gateway(handler=check_bool)) as client:

        response = client.get("/bool?a_value=true")

        assert response.status_code == 200
        assert response.json() == {"value": True}

        response = client.get("/bool?a_value=1")
        assert response.json() == {"value": True}

        response = client.get("/bool?a_value=0")
        assert response.json() == {"value": False}

        response = client.get("/bool?a_value=false")
        assert response.json() == {"value": False}


def test_open_api(test_app_client_factory):
    with create_client(routes=Gateway(handler=check_bool)) as client:
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
                "/bool": {
                    "get": {
                        "summary": "Check Bool",
                        "operationId": "check_bool_bool_get",
                        "parameters": [
                            {
                                "name": "a_value",
                                "in": "query",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {"type": "boolean", "title": "A Value"},
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
                }
            },
        }
