from typing import Dict

from esmerald import Esmerald, Gateway, get
from esmerald.testclient import EsmeraldTestClient
from tests.settings import TestSettings


@get("/bar")
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Esmerald(
    contact={
        "name": "API Support",
        "url": "https://www.example.com",
        "email": "example@example.com",
    },
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    settings_module=TestSettings,
)


client = EsmeraldTestClient(app)


def test_application(test_client_factory):
    response = client.get("/bar")
    assert response.status_code == 200, response.json()


def test_openapi_schema(test_client_factory):
    response = client.get("/openapi.json")

    assert response.status_code == 200, response.text
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Esmerald",
            "summary": "Esmerald application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {
                "name": "API Support",
                "url": "https://www.example.com/",
                "email": "example@example.com",
            },
            "version": client.app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "summary": "Bar",
                    "description": "",
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
