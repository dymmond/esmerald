from typing import Dict, List, Union

from pydantic import BaseModel

from esmerald import Gateway, JSONResponse, get
from esmerald.openapi.datastructures import OpenAPIResponse
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


@get(
    response_class=JsonResponse,
    responses={500: OpenAPIResponse(model=CustomResponse, description="Error")},
)
def read_people() -> Dict[str, str]:
    """ """


@get(
    "/item/{id}",
    responses={422: OpenAPIResponse(model=Error, description="Error")},
)
async def read_item(id: str) -> None:
    """ """


def test_open_api_schema(test_client_factory):
    with create_client(
        routes=[Gateway(handler=read_item), Gateway(handler=read_people)],
        enable_openapi=True,
        include_in_schema=True,
        settings_config=TestSettings,
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
                "/item/{id}": {
                    "get": {
                        "summary": "Read Item",
                        "operationId": "read_item_item__id__get",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {"type": "string", "title": "Id"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "Successful response"},
                            "422": {
                                "description": "Error",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                },
                            },
                        },
                        "deprecated": False,
                    }
                },
                "/": {
                    "get": {
                        "summary": "Read People",
                        "operationId": "read_people__get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/vnd.api+json": {"schema": {"type": "string"}}
                                },
                            },
                            "500": {
                                "description": "Error",
                                "content": {
                                    "application/vnd.api+json": {
                                        "schema": {"$ref": "#/components/schemas/CustomResponse"}
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
                    "CustomResponse": {
                        "properties": {
                            "status": {"type": "string", "title": "Status"},
                            "title": {"type": "string", "title": "Title"},
                            "errors": {
                                "items": {"$ref": "#/components/schemas/Error"},
                                "type": "array",
                                "title": "Errors",
                            },
                        },
                        "type": "object",
                        "required": ["status", "title", "errors"],
                        "title": "CustomResponse",
                    },
                    "Error": {
                        "properties": {
                            "status": {"type": "integer", "title": "Status"},
                            "detail": {"type": "string", "title": "Detail"},
                        },
                        "type": "object",
                        "required": ["status", "detail"],
                        "title": "Error",
                    },
                }
            },
        }
