from typing import Union

from pydantic import BaseModel

from esmerald import Cookie, Gateway, Param, Response, post
from esmerald.datastructures import Cookie as ResponseCookie
from esmerald.responses.encoders import ORJSONResponse
from esmerald.testclient import create_client
from esmerald.utils.enums import MediaType


class User(BaseModel):
    name: str
    email: str


@post(path="/create")
async def create_user(
    data: User,
    cookie: str = Cookie(value="csrftoken"),
) -> ORJSONResponse:
    return ORJSONResponse({"cookie": cookie, "user": data})


def test_cookies_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoken": "my-cookie"})

        assert response.status_code == 201
        assert response.json()["cookie"] == "my-cookie"


def test_cookie_missing_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
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
    data: Item,
    cookie: str = Cookie(value="csrftoken"),
) -> Response:
    return Response(cookie)


def test_response_cookies(test_client_factory):
    data = {"sku": 123}
    with create_client(routes=[Gateway(handler=create_item)]) as client:
        response = client.post("/item", json=data, cookies={"csrftoken": "request"})

        assert response.status_code == 201
        assert response.cookies["token"] == "granted"


@post(path="/create")
async def create_user_with_param(
    data: User,
    cookie: str = Param(cookie="csrftoken"),
) -> ORJSONResponse:
    return ORJSONResponse({"cookie": cookie, "user": data})


def test_cookies_param_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoken": "my-cookie"})

        assert response.status_code == 201
        assert response.json()["cookie"] == "my-cookie"


def test_param_cookie_missing_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, cookies={"csrftoke": "my-cookie"})

        assert response.status_code == 400
