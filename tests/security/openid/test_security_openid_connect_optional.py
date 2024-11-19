from typing import Any, Optional

from pydantic import BaseModel

from esmerald import Gateway, Inject, Injects, Security, get
from esmerald.security.open_id import OpenIdConnect
from esmerald.testclient import create_client

oid = OpenIdConnect(openIdConnectUrl="/openid", auto_error=False)


class User(BaseModel):
    username: str


def get_current_user(oauth_header: Optional[str] = Security(oid)):
    if oauth_header is None:
        return None
    user = User(username=oauth_header)
    return user


@get("/users/me", dependencies={"current_user": Inject(get_current_user)})
def read_current_user(current_user: Optional[User] = Injects()) -> Any:
    if current_user is None:
        return {"msg": "Create an account first"}
    return current_user


def test_security_oauth2():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Bearer footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Bearer footokenbar"}


def test_security_oauth2_password_other_header():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Other footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Other footokenbar"}


def test_security_oauth2_password_bearer_no_header():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
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
                "/users/me": {
                    "get": {
                        "summary": "Read Current User",
                        "description": "",
                        "operationId": "read_current_user_users_me_get",
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
