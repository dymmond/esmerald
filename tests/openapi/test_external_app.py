from typing import Dict, Union

from flask import Flask, request
from markupsafe import escape
from pydantic import BaseModel

from esmerald import JSON, Gateway, Include, get
from esmerald.middleware import WSGIMiddleware
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.testclient import create_client

flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():  # pragma: no cover
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from Flask!"


class Item(BaseModel):
    sku: Union[int, str]


@get()
def read_people() -> Dict[str, str]:
    """ """


@get(
    "/item",
    description="Read an item",
    responses={200: OpenAPIResponse(model=Item, description="The SKU information of an item")},
)
async def read_item() -> JSON:
    """ """


def test_external_app_not_include_in_schema(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include("/child", app=WSGIMiddleware(flask_app)),
        ]
    ) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200, response.text

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
                "/": {
                    "get": {
                        "summary": "Read People",
                        "operationId": "read_people__get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
            },
        }
