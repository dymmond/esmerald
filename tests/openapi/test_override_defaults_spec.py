from typing import Dict

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, post
from esmerald.datastructures.msgspec import Struct
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TestSettings


class PydanticError(BaseModel):
    detail: str
    code: int


class MsgSpecError(Struct):
    detail: str
    code: int


@post(
    "/foo",
    tags=["foo"],
    responses={
        200: OpenAPIResponse(model=MsgSpecError),
        201: OpenAPIResponse(model=PydanticError),
    },
)
async def foo() -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    routes=[Gateway(handler=foo)],
    enable_openapi=True,
    tags=["test"],
    settings_module=TestSettings,
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
            "/foo": {
                "post": {
                    "tags": ["test", "foo"],
                    "summary": "Foo",
                    "description": "",
                    "operationId": "foo_foo_post",
                    "responses": {
                        "201": {
                            "description": "Additional response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        },
                        "200": {
                            "description": "Additional response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MsgSpecError"}
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
                "MsgSpecError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "MsgSpecError",
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
            }
        },
        "tags": ["test"],
    }
