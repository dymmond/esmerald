from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest
from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass

from esmerald import Form, Gateway, post, route
from esmerald.exceptions import ImproperlyConfigured
from esmerald.testclient import create_client


@pydantic_dataclass
class User:
    id: int
    name: str


@dataclass
class UserOut:
    id: int
    name: str


class UserModel(BaseModel):
    id: int
    name: str


@post("/form")
async def test_form(data: Any = Form()) -> Dict[str, str]:
    return {"name": data["name"]}


@post("/complex-form-pydantic")
async def test_complex_form_pydantic_dataclass(data: User = Form()) -> User:
    return data


@post("/complex-form-dataclass")
async def test_complex_form_dataclass(data: UserOut = Form()) -> UserOut:
    return data


@post("/complex-form-basemodel")
async def test_complex_form_basemodel(data: UserModel = Form()) -> UserModel:
    return data


def test_send_form(test_client_factory):
    data = {"name": "Test"}

    with create_client(routes=[Gateway(handler=test_form)]) as client:
        response = client.post("/form", data=data)

        assert response.status_code == 201
        assert response.json() == {"name": "Test"}


def test_send_complex_form_pydantic_dataclass(test_client_factory):
    data = {"id": 1, "name": "Test"}
    with create_client(
        routes=[Gateway(handler=test_complex_form_pydantic_dataclass)],
        enable_openapi=True,
    ) as client:
        response = client.post("/complex-form-pydantic", data=data)
        assert response.status_code == 201, response.text
        assert response.json() == {"id": 1, "name": "Test"}


def test_send_complex_form_normal_dataclass(test_client_factory):
    data = {"id": 1, "name": "Test"}
    with create_client(
        routes=[Gateway(handler=test_complex_form_dataclass)],
        enable_openapi=True,
    ) as client:
        response = client.post("/complex-form-dataclass", data=data)
        assert response.status_code == 201, response.text
        assert response.json() == {"id": 1, "name": "Test"}


def test_send_complex_form_base_model(test_client_factory):
    data = {"id": 1, "name": "Test"}
    with create_client(
        routes=[Gateway(handler=test_complex_form_basemodel)],
        enable_openapi=True,
    ) as client:
        response = client.post("/complex-form-basemodel", data=data)
        assert response.status_code == 201, response.text
        assert response.json() == {"id": 1, "name": "Test"}


def test_get_and_head_data():
    with pytest.raises(ImproperlyConfigured):

        @route(methods=["GET", "HEAD"])
        async def start(data: Optional[UserModel]) -> bytes:
            return b"hello world"
