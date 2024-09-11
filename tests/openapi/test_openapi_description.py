from esmerald import Esmerald, Gateway, get
from esmerald.testclient import EsmeraldTestClient


@get(description="home from handler")
async def home() -> None: ...


@get()
async def item() -> None:
    """item from docstring"""


@get()
async def no_desc() -> None: ...


app = Esmerald(
    routes=[
        Gateway("/home", handler=home),
        Gateway("/item", handler=item),
        Gateway("/no-desc", handler=no_desc),
    ],
    enable_openapi=True,
)
client = EsmeraldTestClient(app)


def test_openapi_schema_operation_ids_when_same_handler_is_used(test_client_factory):
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
            "/home": {
                "get": {
                    "summary": "Home",
                    "description": "home from handler",
                    "operationId": "home_home_get",
                    "responses": {"200": {"description": "Successful response"}},
                    "deprecated": False,
                }
            },
            "/item": {
                "get": {
                    "summary": "Item",
                    "description": "item from docstring",
                    "operationId": "item_item_get",
                    "responses": {"200": {"description": "Successful response"}},
                    "deprecated": False,
                }
            },
            "/no-desc": {
                "get": {
                    "summary": "No Desc",
                    "operationId": "no_desc_no_desc_get",
                    "responses": {"200": {"description": "Successful response"}},
                    "deprecated": False,
                }
            },
        },
    }
