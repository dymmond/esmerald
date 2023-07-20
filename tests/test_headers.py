from typing import Union

from pydantic import BaseModel

from esmerald import Gateway, Header, Param, Response, post
from esmerald.datastructures import ResponseHeader
from esmerald.enums import MediaType
from esmerald.responses.encoders import ORJSONResponse
from esmerald.testclient import create_client


class User(BaseModel):
    name: str
    email: str


@post(path="/create")
async def create_user(
    data: User,
    token: str = Header(value="X-API-TOKEN"),
) -> ORJSONResponse:
    return ORJSONResponse({"token": token, "user": data})


def test_headers_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user)]) as client:
        response = client.post("/create", json=user, headers={"X-API-TOKEN": "my-token"})

        assert response.status_code == 201
        assert response.json()["token"] == "my-token"


def test_headers_missing_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user)]) as client:
        response = client.post("/create", json=user, headers={"X-API-TOKE": "my-token"})

        assert response.status_code == 400


class Item(BaseModel):
    sku: Union[str, int]


@post(
    path="/item",
    response_headers={"sku": ResponseHeader(value="123")},
    media_type=MediaType.JSON,
)
async def create_item(
    data: Item,
    token: str = Header(value="X-API-TOKEN"),
) -> Response:
    return Response("ok")


def test_response_headers(test_client_factory):
    data = {"sku": 123}
    with create_client(routes=[Gateway(handler=create_item)]) as client:
        response = client.post("/item", json=data, headers={"X-API-TOKEN": "my-token"})

        assert response.status_code == 201
        assert response.headers["sku"] == "123"


@post(path="/create")
async def create_user_with_param(
    data: User,
    token: str = Param(header="X-API-TOKEN"),
) -> ORJSONResponse:
    return ORJSONResponse({"token": token, "user": data})


def test_headers_param_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, headers={"X-API-TOKEN": "my-token"})

        assert response.status_code == 201
        assert response.json()["token"] == "my-token"


def test_param_header_missing_field(test_client_factory):
    user = {"name": "Esmerald", "email": "test@esmerald.com"}
    with create_client(routes=[Gateway(handler=create_user_with_param)]) as client:
        response = client.post("/create", json=user, headers={"X-API-TOKE": "my-token"})

        assert response.status_code == 400
