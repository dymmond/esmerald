from base64 import b64encode
from typing import Any, Optional

from ravyn import Gateway, Inject, Injects, get
from ravyn.security.http import HTTPBasic, HTTPBasicCredentials
from ravyn.testclient import create_client

security = HTTPBasic(auto_error=False)


@get(
    "/users/me",
    security=[security],
    dependencies={"credentials": Inject(security)},
)
def read_current_user(credentials: Optional[HTTPBasicCredentials] = Injects()) -> Any:
    if credentials is None:
        return {"msg": "Create an account first"}
    return {"username": credentials.username, "password": credentials.password}


def test_security_http_basic():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
    ) as client:
        response = client.get("/users/me", auth=("john", "secret"))
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "john", "password": "secret"}


def test_security_http_basic_no_credentials():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_security_http_basic_invalid_credentials():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me", headers={"Authorization": "Basic notabase64token"})
        assert response.status_code == 401, response.text
        assert response.headers["WWW-Authenticate"] == "Basic"
        assert response.json() == {"detail": "Invalid authentication credentials"}


def test_security_http_basic_non_basic_credentials():
    payload = b64encode(b"johnsecret").decode("ascii")
    auth_header = f"Basic {payload}"

    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me", headers={"Authorization": auth_header})
        assert response.status_code == 401, response.text
        assert response.headers["WWW-Authenticate"] == "Basic"
        assert response.json() == {"detail": "Invalid authentication credentials"}


def test_openapi_schema():
    with create_client(routes=[Gateway(handler=read_current_user)], enable_openapi=True) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200, response.text

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Ravyn",
                "summary": "Ravyn application",
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
                        "deprecated": False,
                        "security": [
                            {
                                "HTTPBasic": {
                                    "type": "http",
                                    "scheme": "basic",
                                    "scheme_name": "HTTPBasic",
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
            "components": {"securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}},
        }
