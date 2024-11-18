from typing import Any, Dict, Optional

from esmerald import Gateway, Inject, Injects, get
from esmerald.security.oauth2 import OAuth2PasswordBearer
from esmerald.testclient import create_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


@get("/items/", security=[oauth2_scheme], dependencies={"token": Inject(oauth2_scheme)})
async def read_items(token: Optional[str] = Injects()) -> Dict[str, Any]:
    if token is None:
        return {"msg": "Create an account first"}
    return {"token": token}


def test_no_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200, response.text
        assert response.json() == {"token": "testtoken"}


def test_incorrect_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Notexistent testtoken"})
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
        enable_openapi=True,
    ) as client:
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
                "/items": {
                    "get": {
                        "summary": "Read Items",
                        "description": "",
                        "operationId": "read_items_items_get",
                        "deprecated": False,
                        "security": [
                            {
                                "OAuth2PasswordBearer": {
                                    "type": "oauth2",
                                    "flows": {"password": {"tokenUrl": "/token", "scopes": {}}},
                                    "scheme_name": "OAuth2PasswordBearer",
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "OAuth2PasswordBearer": {
                        "type": "oauth2",
                        "flows": {"password": {"tokenUrl": "/token", "scopes": {}}},
                    }
                }
            },
        }
