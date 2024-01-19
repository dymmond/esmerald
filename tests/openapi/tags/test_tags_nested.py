from typing import Dict

from esmerald import Esmerald, Gateway, get
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TestSettings


@get("/bar")
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_config=TestSettings,
)


def test_openapi_schema_tags(test_client_factory):
    client = EsmeraldTestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200, response.text
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Esmerald",
            "summary": "Esmerald application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "admin", "email": "admin@myapp.com"},
            "version": app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "tags": ["test"],
                    "summary": "Bar",
                    "operationId": "bar_bar_get",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {"schema": {"type": "string"}}},
                        }
                    },
                    "deprecated": False,
                }
            }
        },
        "tags": ["test"],
    }
