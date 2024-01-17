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
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_config=TestSettings,
    contact={"name": "esmerald", "email": "esmerald@esmeral.dev"},
)


client = EsmeraldTestClient(app)


def test_openapi_schema_tags_pydantic(test_client_factory):
    response = client.get("/openapi.json")

    assert response.status_code == 200, response.text

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Esmerald",
            "summary": "Esmerald application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "esmerald", "email": "esmerald@esmeral.dev"},
            "version": app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "tags": ["test", "bar"],
                    "summary": "Bar",
                    "operationId": "bar_bar_get",
                    "responses": {
                        "200": {
                            "description": "Pydantic response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        }
                    },
                    "deprecated": False,
                }
            }
        },
        "components": {
            "schemas": {
                "PydanticError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "PydanticError",
                }
            }
        },
        "tags": ["test"],
    }
