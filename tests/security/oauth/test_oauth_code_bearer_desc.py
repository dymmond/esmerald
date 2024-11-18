from typing import Any, Optional

from esmerald import Gateway, Inject, Injects, get
from esmerald.security.oauth2 import OAuth2AuthorizationCodeBearer
from esmerald.testclient import create_client

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="authorize",
    tokenUrl="token",
    description="OAuth2 Code Bearer",
    auto_error=True,
)


@get("/items", dependencies={"token": Inject(oauth2_scheme)}, security=[oauth2_scheme])
async def read_items(token: Optional[str] = Injects()) -> dict[str, Any]:
    return {"token": token}


def test_no_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Non-existent testtoken"})
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_token():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
    ) as client:
        response = client.get("/items", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200, response.text
        assert response.json() == {"token": "testtoken"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_items),
        ],
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
                                "OAuth2AuthorizationCodeBearer": {
                                    "type": "oauth2",
                                    "description": "OAuth2 Code Bearer",
                                    "flows": {
                                        "authorizationCode": {
                                            "authorizationUrl": "authorize",
                                            "tokenUrl": "token",
                                            "scopes": {},
                                        }
                                    },
                                    "scheme_name": "OAuth2AuthorizationCodeBearer",
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
                    "OAuth2AuthorizationCodeBearer": {
                        "type": "oauth2",
                        "description": "OAuth2 Code Bearer",
                        "flows": {
                            "authorizationCode": {
                                "authorizationUrl": "authorize",
                                "tokenUrl": "token",
                                "scopes": {},
                            }
                        },
                    }
                }
            },
        }
