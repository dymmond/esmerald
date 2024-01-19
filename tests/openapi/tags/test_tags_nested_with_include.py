from typing import Dict

from esmerald import Esmerald, Gateway, Include, get
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TestSettings


@get("/bar")
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    routes=[Include("/api/v2", routes=[Include(routes=[Gateway(handler=bar)])], tags=["Include"])],
    enable_openapi=True,
    settings_config=TestSettings,
)


def test_openapi_schema_tags_include(test_client_factory):
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
            "/api/v2/bar": {
                "get": {
                    "tags": ["Include"],
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
    }
