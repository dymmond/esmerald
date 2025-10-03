from typing import Union

from pydantic import BaseModel

from ravyn import Cookie, Gateway, Param, Response, post
from ravyn.core.datastructures import Cookie as ResponseCookie
from ravyn.responses.encoders import ORJSONResponse
from ravyn.testclient import create_client
from ravyn.utils.enums import MediaType


class User(BaseModel):
    name: str
    email: str


@post(path="/create")
async def create_user(
    payload: User,
    cookie: str = Cookie(value="csrftoken"),
) -> ORJSONResponse:
    return ORJSONResponse({"cookie": cookie, "user": payload})


def test_cookies_field(test_client_factory):
    user = {"name": "Ravyn", "email": "test@ravyn.com"}
    with create_client(routes=[Gateway(handler=create_user)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoken": "my-cookie"})

        assert response.status_code == 201
        assert response.json()["cookie"] == "my-cookie"


def test_cookie_missing_field(test_client_factory):
    user = {"name": "Ravyn", "email": "test@ravyn.com"}
    with create_client(routes=[Gateway(handler=create_user)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoke": "my-token"})

        assert response.status_code == 400


class Item(BaseModel):
    sku: Union[str, int]


@post(
    path="/item",
    response_cookies=[ResponseCookie(key="token", value="granted", max_age=3000, httponly=True)],
    media_type=MediaType.JSON,
)
async def create_item(
    payload: Item,
    cookie: str = Cookie(value="csrftoken"),
) -> Response:
    return Response(cookie)


def test_response_cookies(test_client_factory):
    payload = {"sku": 123}
    with create_client(routes=[Gateway(handler=create_item)]) as client:
        response = client.post("/item", json=payload, cookies={"csrftoken": "request"})

        assert response.status_code == 201
        assert response.cookies["token"] == "granted"


@post(path="/create")
async def create_user_with_param(
    payload: User,
    cookie: str = Param(cookie="csrftoken"),
) -> ORJSONResponse:
    return ORJSONResponse({"cookie": cookie, "user": payload})


def test_cookies_param_field(test_client_factory):
    user = {"name": "Ravyn", "email": "test@ravyn.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoken": "my-cookie"})

        assert response.status_code == 201
        assert response.json()["cookie"] == "my-cookie"


def test_param_cookie_missing_field(test_client_factory):
    user = {"name": "Ravyn", "email": "test@ravyn.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoke": "my-cookie"})

        assert response.status_code == 400
