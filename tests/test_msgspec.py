from typing import Union

from msgspec import Struct

# from pydantic import BaseModel
from starlette import status

from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import post
from esmerald.testclient import create_client


class User(Struct):
    name: str
    email: Union[str, None] = None


# class BaseUser(BaseModel):
#     model_config = {"arbitrary_types_allowed": True}
#     user: User


@post(status_code=status.HTTP_202_ACCEPTED)
def get_user(payload: User) -> User:
    return payload


# @post(status_code=status.HTTP_202_ACCEPTED)
# def user(payload: BaseUser) -> User:
#     return payload


def test_user_msgspec(test_client_factory):
    with create_client(routes=[Gateway(handler=get_user)]) as client:
        data = {"name": "Esmerald", "email": "esmerald@esmerald.dev"}
        response = client.post("/", json=data)

        assert response.json() == data


def test_user_msgspec_raise_validation_error(test_client_factory):
    with create_client(routes=[Gateway(handler=get_user)]) as client:
        data = {"name": 1, "email": "esmerald@esmerald.dev"}
        response = client.post("/", json=data)

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Validation failed for http://testserver/ with method POST.",
            "errors": [{"name": "Expected `str`, got `int`"}],
        }


# def test_user_msgspec_two(test_client_factory):
#     with create_client(routes=[Gateway(handler=user)]) as client:
#         data = {"user": {"name": "Esmerald", "email": "esmerald@esmerald.dev"}}
#         response = client.post("/", json=data)
#         breakpoint()
#         assert response.json() == data
