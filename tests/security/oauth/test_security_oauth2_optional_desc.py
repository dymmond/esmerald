from typing import Any, Dict, Optional, Union

import pytest
from pydantic import BaseModel, __version__

from ravyn import Gateway, Inject, Injects, Security, get, post
from ravyn.security.oauth2 import OAuth2, OAuth2PasswordRequestFormStrict
from ravyn.testclient import create_client

pydantic_version = ".".join(__version__.split(".")[:2])

reusable_oauth2 = OAuth2(
    flows={
        "password": {
            "tokenUrl": "token",
            "scopes": {"read:users": "Read the users", "write:users": "Create users"},
        }
    },
    description="OAuth2 security scheme",
    auto_error=False,
)


class User(BaseModel):
    username: str


def get_current_user(oauth_header: Union[str, Any] = Security(reusable_oauth2)):
    if oauth_header is None:
        return None
    user = User(username=oauth_header)
    return user


@post(
    "/login",
    security=[reusable_oauth2],
    dependencies={"form_data": Inject(OAuth2PasswordRequestFormStrict)},
)
def login(form_data: OAuth2PasswordRequestFormStrict = Injects()) -> Dict[str, Any]:
    return form_data


@get(
    "/users/me",
    dependencies={"current_user": Inject(get_current_user)},
    security=[reusable_oauth2],
)
def read_users_me(current_user: Optional[User] = Injects()) -> Dict[str, Any]:
    if current_user is None:
        return {"msg": "Create an account first"}
    return current_user


def test_security_oauth2():
    with create_client(
        routes=[Gateway(handler=read_users_me)], security=[reusable_oauth2]
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Bearer footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Bearer footokenbar"}


def test_security_oauth2_password_other_header():
    with create_client(
        routes=[Gateway(handler=read_users_me)], security=[reusable_oauth2]
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Other footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Other footokenbar"}


def test_security_oauth2_password_bearer_no_header():
    with create_client(
        routes=[Gateway(handler=read_users_me)], security=[reusable_oauth2]
    ) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_strict_login_None():
    with create_client(routes=[Gateway(handler=login)], security=[reusable_oauth2]) as client:
        response = client.post("/login", data=None)
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Validation failed for http://testserver/login with method POST.",
            "errors": [
                {
                    "type": "string_type",
                    "loc": ["grant_type"],
                    "msg": "Input should be a valid string",
                    "input": None,
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/string_type",
                },
                {
                    "type": "string_type",
                    "loc": ["username"],
                    "msg": "Input should be a valid string",
                    "input": None,
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/string_type",
                },
                {
                    "type": "string_type",
                    "loc": ["password"],
                    "msg": "Input should be a valid string",
                    "input": None,
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/string_type",
                },
            ],
        }


def test_strict_login_no_grant_type():
    with create_client(routes=[Gateway(handler=login)], security=[reusable_oauth2]) as client:
        response = client.post("/login", json={"username": "johndoe", "password": "secret"})
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Validation failed for http://testserver/login with method POST.",
            "errors": [
                {
                    "type": "string_type",
                    "loc": ["grant_type"],
                    "msg": "Input should be a valid string",
                    "input": None,
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/string_type",
                }
            ],
        }


@pytest.mark.parametrize(
    argnames=["grant_type"],
    argvalues=[
        pytest.param("incorrect", id="incorrect value"),
        pytest.param("passwordblah", id="password with suffix"),
        pytest.param("blahpassword", id="password with prefix"),
    ],
)
def test_strict_login_incorrect_grant_type(grant_type):
    with create_client(routes=[Gateway(handler=login)], security=[reusable_oauth2]) as client:
        response = client.post(
            "/login",
            json={"username": "johndoe", "password": "secret", "grant_type": grant_type},
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Validation failed for http://testserver/login with method POST.",
            "errors": [
                {
                    "type": "string_pattern_mismatch",
                    "loc": ["grant_type"],
                    "msg": "String should match pattern '^password$'",
                    "input": grant_type,
                    "ctx": {"pattern": "^password$"},
                    "url": f"https://errors.pydantic.dev/{pydantic_version}/v/string_pattern_mismatch",
                }
            ],
        }


def test_strict_login_correct_correct_grant_type():
    with create_client(routes=[Gateway(handler=login)], security=[reusable_oauth2]) as client:
        response = client.post(
            "/login",
            json={"username": "johndoe", "password": "secret", "grant_type": "password"},
        )
        assert response.status_code == 201, response.text
        assert response.json() == {
            "grant_type": "password",
            "username": "johndoe",
            "password": "secret",
            "scopes": [],
            "client_id": None,
            "client_secret": None,
        }
