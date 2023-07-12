from typing import Dict, Union

from pydantic import BaseModel

from esmerald import Gateway, JSONResponse, get
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.testclient import create_client


class CustomResponse(BaseModel):
    status: str
    title: str


class JsonResponse(JSONResponse):
    media_type: str = "application/vnd.api+json"


class Item(BaseModel):
    sku: Union[int, str]


@get()
def read_people() -> Dict[str, str]:
    return {"id": "foo"}


@get(
    "/item/{id}",
    response_class=JsonResponse,
    responses={422: OpenAPIResponse(model=CustomResponse, description="Error")},
)
async def read_item(id: str) -> None:
    ...


def test_open_api_schema(test_client_factory):
    with create_client(
        routes=[Gateway(handler=read_item)], enable_openapi=True, include_in_schema=True
    ) as client:
        response = client.get("/openapi.json")

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Esmerald",
                "summary": "Esmerald application",
                "description": "test_client",
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
                            "200": {
                                "description": "Successful response",
                                "content": {"application/vnd.api+json": {"schema": {}}},
                            },
                            "422": {
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
                }
            },
            "components": {
                "schemas": {
                    "CustomResponse": {
                        "properties": {
                            "status": {"type": "string", "title": "Status"},
                            "title": {"type": "string", "title": "Title"},
                        },
                        "type": "object",
                        "required": ["status", "title"],
                        "title": "CustomResponse",
                    }
                }
            },
        }
